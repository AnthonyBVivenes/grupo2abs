"""Canal de red robusto para multijugador remoto (TCP/LAN).

Protocolo v2:
- Handshake: HELLO -> WELCOME -> GAME_START (con ACK)
- Heartbeat: PING/PONG cada 2s, timeout 6s
- Mensajes críticos con ACK y número de secuencia
- Host es autoridad absoluta del estado del juego
- Reconexión básica con token de sesión
"""
import json
import queue
import socket
import threading
import time
import uuid

_ACCEPT_TIMEOUT = 0.2
_CONNECT_TIMEOUT = 4.0
_HEARTBEAT_INTERVAL = 2.0
_HEARTBEAT_TIMEOUT = 6.0
_ACK_TIMEOUT = 3.0
_MAX_RETRIES = 3


def encode(data):
    return (json.dumps(data) + "\n").encode("utf-8")


def local_ips():
    """Direcciones IPv4 locales útiles para compartir el modo host."""
    ips = ["127.0.0.1"]
    try:
        for name in socket.getaddrinfo(socket.gethostname(), None,
                                       socket.AF_INET, socket.SOCK_STREAM):
            ip = name[4][0]
            if not ip.startswith("127.") and ip not in ips:
                ips.append(ip)
    except OSError:
        pass
    return ips


class Message:
    """Representa un mensaje del protocolo con metadatos."""

    def __init__(self, mtype, payload=None, seq=None, ack_seq=None, session_id=None):
        self.type = mtype
        self.payload = payload or {}
        self.seq = seq
        self.ack_seq = ack_seq
        self.session_id = session_id
        self.timestamp = time.time()
        self.retries = 0

    def to_dict(self):
        d = {"type": self.type, "payload": self.payload}
        if self.seq is not None:
            d["seq"] = self.seq
        if self.ack_seq is not None:
            d["ack_seq"] = self.ack_seq
        if self.session_id is not None:
            d["session_id"] = self.session_id
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(
            mtype=d.get("type"),
            payload=d.get("payload", {}),
            seq=d.get("seq"),
            ack_seq=d.get("ack_seq"),
            session_id=d.get("session_id")
        )

    def __repr__(self):
        return f"Message(type={self.type}, seq={self.seq}, ack={self.ack_seq})"


class RemotePeer:
    """Conexión TCP con cola de mensajes entrantes, heartbeat y ACKs."""

    def __init__(self, sock, is_host=False):
        self.sock = sock
        self.is_host = is_host
        try:
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError:
            pass
        self._send_lock = threading.Lock()
        self._queue = queue.Queue()
        self._closed = False
        self._seq_counter = 0
        self._pending_acks = {}  # seq -> Message
        self._last_pong = time.time()
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._ack_thread = threading.Thread(target=self._ack_retry_loop, daemon=True)
        self._read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._read_thread.start()
        self._heartbeat_thread.start()
        self._ack_thread.start()

    def _next_seq(self):
        self._seq_counter += 1
        return self._seq_counter

    def _read_loop(self):
        buf = b""
        try:
            while not self._closed:
                chunk = self.sock.recv(4096)
                if not chunk:
                    print("[DEBUG peer] recv empty -> connection closed by remote")
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line.decode("utf-8"))
                        msg = Message.from_dict(data)
                    except (ValueError, UnicodeDecodeError) as e:
                        print(f"[DEBUG peer] decode error: {e}")
                        continue
                    self._handle_incoming(msg)
        except OSError as e:
            if not self._closed:
                print(f"[DEBUG peer] OSError in read_loop: {e}")
        except Exception as e:
            print(f"[DEBUG peer] unexpected error in read_loop: {e}")
        finally:
            self._close_internal()

    def _handle_incoming(self, msg):
        """Procesa mensaje entrante: ACKs, PING/PONG, y mensajes de aplicación."""
        # ACK recibido para un mensaje nuestro
        if msg.ack_seq is not None and msg.type != "PONG":
            with self._send_lock:
                pending = self._pending_acks.pop(msg.ack_seq, None)
                if pending:
                    print(f"[DEBUG peer] ACK received for seq={msg.ack_seq}")

        # PONG recibido (heartbeat response)
        if msg.type == "PONG":
            self._last_pong = time.time()
            return

        # PING recibido -> responder PONG
        if msg.type == "PING":
            self._send_raw(Message("PONG", seq=msg.seq, ack_seq=msg.seq))
            return

        # Mensaje con secuencia -> enviar ACK
        if msg.seq is not None and msg.type not in ("PING", "PONG"):
            self._send_raw(Message("ACK", ack_seq=msg.seq))

        # Encolar para la aplicación
        self._queue.put(msg)

    def _send_raw(self, msg):
        """Envío bajo nivel sin lógica de reintento (para ACKs, PONG)."""
        if self._closed:
            return False
        try:
            payload = encode(msg.to_dict())
            with self._send_lock:
                self.sock.sendall(payload)
            return True
        except OSError:
            self._close_internal()
            return False

    def send(self, mtype, payload=None, require_ack=False, session_id=None):
        """Envía mensaje de aplicación. Si require_ack, usa secuencia y reintenta."""
        if self._closed:
            return False

        seq = self._next_seq() if require_ack else None
        msg = Message(mtype, payload, seq=seq, session_id=session_id)

        if require_ack:
            with self._send_lock:
                self._pending_acks[seq] = msg

        return self._send_raw(msg)

    def _ack_retry_loop(self):
        """Reintenta mensajes pendientes de ACK."""
        while not self._closed:
            time.sleep(0.1)
            now = time.time()
            with self._send_lock:
                for seq, msg in list(self._pending_acks.items()):
                    if now - msg.timestamp > _ACK_TIMEOUT:
                        if msg.retries >= _MAX_RETRIES:
                            print(f"[DEBUG peer] max retries reached for seq={seq}, closing")
                            self._close_internal()
                            return
                        msg.retries += 1
                        msg.timestamp = now
                        print(f"[DEBUG peer] retry {msg.retries}/{_MAX_RETRIES} for seq={seq} type={msg.type}")
                        self._send_raw(msg)

    def _heartbeat_loop(self):
        """Envía PING periódicamente y detecta timeout."""
        while not self._closed:
            time.sleep(_HEARTBEAT_INTERVAL)
            if self._closed:
                break
            if time.time() - self._last_pong > _HEARTBEAT_TIMEOUT:
                print("[DEBUG peer] heartbeat timeout, closing connection")
                self._close_internal()
                return
            self.send("PING", require_ack=False)

    def poll(self):
        msgs = []
        while True:
            try:
                msgs.append(self._queue.get_nowait())
            except queue.Empty:
                return msgs

    def close(self):
        self._close_internal()

    def _close_internal(self):
        if self._closed:
            return
        self._closed = True
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            self.sock.close()
        except OSError:
            pass
        # Notificar a la aplicación
        self._queue.put(Message("DISCONNECT"))


class RemoteHost:
    """Anfitrión: escucha en background y acepta la primera conexión."""

    def __init__(self, port):
        self.error = None
        self.peer = None
        self._closed = False
        self.session_id = str(uuid.uuid4())[:8]
        self._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._listener.bind(("", port))
            self._listener.listen(1)
            self._listener.settimeout(_ACCEPT_TIMEOUT)
            self.bound_port = self._listener.getsockname()[1]
        except OSError as exc:
            self.error = str(exc)
            self.bound_port = port
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self):
        while not self._closed and self.peer is None and not self.error:
            try:
                conn, _addr = self._listener.accept()
                if self.peer is None:
                    self.peer = RemotePeer(conn, is_host=True)
            except socket.timeout:
                continue
            except OSError as exc:
                self.error = str(exc)

    def connected(self):
        return self.peer is not None and not self.peer._closed

    def send(self, mtype, payload=None, require_ack=False):
        if self.peer:
            return self.peer.send(mtype, payload, require_ack, session_id=self.session_id)
        return False

    def poll(self):
        if self.peer:
            return self.peer.poll()
        return []

    def close(self):
        self._closed = True
        try:
            self._listener.close()
        except OSError:
            pass
        if self.peer:
            self.peer.close()


class RemoteClient:
    """Invitado: conecta en background sin bloquear la interfaz."""

    def __init__(self, host, port, timeout=_CONNECT_TIMEOUT):
        self.error = None
        self.peer = None
        self.session_id = None
        threading.Thread(target=self._connect, daemon=True,
                         args=(host, port, timeout)).start()

    def _connect(self, host, port, timeout):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
            sock.settimeout(None)
            self.peer = RemotePeer(sock, is_host=False)
        except OSError as exc:
            self.error = str(exc)
            try:
                sock.close()
            except OSError:
                pass

    def connected(self):
        return self.peer is not None and not self.peer._closed

    def send(self, mtype, payload=None, require_ack=False):
        if self.peer:
            return self.peer.send(mtype, payload, require_ack, session_id=self.session_id)
        return False

    def poll(self):
        if self.peer:
            return self.peer.poll()
        return []

    def close(self):
        if self.peer:
            self.peer.close()