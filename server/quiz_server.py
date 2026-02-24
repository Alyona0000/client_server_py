import socket
import re
from typing import Optional, Tuple
from session import LoginSystem

# -------------------- helpers --------------------

_SEPARATORS_RE = re.compile(r"""[ \t!?.,+:;"'()\-]+""")

def normalize_text(s: str) -> str:
    s = _SEPARATORS_RE.sub("", s)
    return s.lower()

def send_response(conn: socket.socket, status: str, payload: str) -> None:
    """
    ЄДИНИЙ протокол відповіді:
    STATUS|payload\n<<ENDOFTEXT>>\n
    payload може бути багаторядковим.
    """
    msg = f"{status}|{payload}\n<<ENDOFTEXT>>\n"
    conn.sendall(msg.encode("utf-8"))

def recv_line(conn: socket.socket, buffer: bytearray) -> Optional[str]:
    """
    Читає до '\n'. Повертає строку без '\r', або None якщо клієнт відвалився.
    """
    while True:
        nl = buffer.find(b"\n")
        if nl != -1:
            raw = buffer[:nl]
            del buffer[:nl + 1]
            return raw.decode("utf-8", errors="replace").rstrip("\r")

        chunk = conn.recv(1024)
        if not chunk:
            return None
        buffer.extend(chunk)

def parse_request_line(line: str) -> Tuple[str, str]:
    """
    Підтримує:
      CMD|payload
      CMD payload
      CMD
    """
    line = line.strip()
    if not line:
        return "", ""

    if "|" in line:
        cmd, payload = line.split("|", 1)
        return cmd.strip().upper(), payload.strip()

    if " " in line:
        cmd, payload = line.split(" ", 1)
        return cmd.strip().upper(), payload.strip()

    return line.upper(), ""

# -------------------- server logic --------------------

def handle_client(conn: socket.socket, addr) -> None:
    print(f"Connected by {addr}")
    buffer = bytearray()

    session = LoginSystem()
    send_response(conn, "OK", session.welcome_message())
   
    try:
        while True:
            line = recv_line(conn, buffer)
            if line is None:
                print(f"Client {addr} disconnected")
                return

            cmd, payload = parse_request_line(line)

            if not cmd:
                send_response(conn, "ERR", "Empty request")
                continue

            # QUIT
            if cmd == "QUIT":
                send_response(conn, "OK", "Goodbye!")
                return

            try:
                response = session.process_command(cmd, payload)
                send_response(conn, "OK", response)
            except ValueError as e:
                send_response(conn, "ERR", str(e))  
            except Exception as e:
                send_response(conn, "ERR", f"invalid arguments: {e}")
                


    finally:
        conn.close()


def main() -> None:
    HOST = ""
    PORT = 20002

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        print(f"Server listening on {HOST!r}:{PORT}")

        while True:
            conn, addr = s.accept()
            handle_client(conn, addr)


if __name__ == "__main__":
    main()