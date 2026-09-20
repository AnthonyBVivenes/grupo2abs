"""Canal de red minimalista para el multijugador remoto (TCP/LAN).

Cada extremo es un RemotePeer: envia mensajes JSON por linea y recibe en un
hilo de fondo, encolando los mensajes que el juego consume cada frame.
Solo socket de la stdlib, sin dependencias.
"""
import json
import queue
import socket
import threading

_ACCEPT_TIMEOUT = 0.2
_CONNECT_TIMEOUT = 4.0


def encode(data):
    return (json.dumps(data) + "\n").encode("utf-8")


def local_ips():
    """Direcciones IPv4 locales utiles para compartir el modo host."""
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


class RemotePeer:
    """Conexion TCP con cola de mensajes entrantes."""

    def __init__(self, sock):
        self.sock = sock
        try:
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError:
            pass
        self._send_lock = threading.Lock()
        self._queue = queue.Queue()
        self._closed = False
        threading.Thread(target=self._read_loop, daemon=True).start()

    def _read_loop(self):
        buf = b""
        try:
            while True:
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
                        msg = json.loads(line.decode("utf-8"))
                    except (ValueError, UnicodeDecodeError) as e:
                        print(f"[DEBUG peer] decode error: {e}")
                        continue
                    self._queue.put(msg)
        except OSError as e:
            print(f"[DEBUG peer] OSError in read_loop: {e}")
        except Exception as e:
            print(f"[DEBUG peer] unexpected error in read_loop: {e}")
        finally:
            self._closed = True
            self._queue.put({"type": "DISCONNECT"})

    def send(self, data):
        if self._closed:
            return False
        try:
            payload = encode(data)
            with self._send_lock:
                self.sock.sendall(payload)
            return True
        except OSError:
            return False

    def poll(self):
        msgs = []
        while True:
            try:
                msgs.append(self._queue.get_nowait())
            except queue.Empty:
                return msgs

    def close(self):
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


class RemoteHost:
    """Anfitrion: escucha en background y acepta la primera conexion."""

    def __init__(self, port):
        self.error = None
        self.peer = None
        self._closed = False
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
                    self.peer = RemotePeer(conn)
            except socket.timeout:
                continue
            except OSError as exc:
                self.error = str(exc)

    def connected(self):
        return self.peer is not None

    def send(self, data):
        if self.peer:
            return self.peer.send(data)
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
        threading.Thread(target=self._connect, daemon=True,
                         args=(host, port, timeout)).start()

    def _connect(self, host, port, timeout):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
            sock.settimeout(None)  # quitar timeout tras conectar
            self.peer = RemotePeer(sock)
        except OSError as exc:
            self.error = str(exc)
            try:
                sock.close()
            except OSError:
                pass

    def connected(self):
        return self.peer is not None

    def send(self, data):
        if self.peer:
            return self.peer.send(data)
        return False

    def poll(self):
        if self.peer:
            return self.peer.poll()
        return []

    def close(self):
        if self.peer:
            self.peer.close()