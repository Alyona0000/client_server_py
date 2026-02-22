# server.py
import socket
import re
from session import LoginSystem

_SEPARATORS_RE = re.compile(r"""[ \t!?.,+:;"'()\-]+""")

def normalize_text(s: str) -> str:
    s = _SEPARATORS_RE.sub("", s)
    return s.lower()

def cmd_pal(payload: str) -> str:
    t = normalize_text(payload)
    return "1" if t == t[::-1] else "0"

def cmd_rev(payload: str) -> str:
    return payload[::-1]

def cmd_words(payload: str) -> str:
    return str(len(payload.split()))

def cmd_vowels(payload: str) -> str:
    vowels = set("aeiouyAEIOUY" "аеиіоуяюєїАЕИІОУЯЮЄЇ")
    return str(sum(1 for ch in payload if ch in vowels))

def cmd_kvodrik(payload: str) -> str:
    n = int(payload.strip())
    return str(n * n)

def cmd_quiz(payload: str) -> str:
    questions = [
        {"q": "1) 2+3 = ?", "opts": "A)2  B)3  C)5", "a": "C"},
        {"q": "2) 5*2 = ?", "opts": "A)7  B)10  C)12", "a": "B"},
        {"q": "3) 9-4 = ?", "opts": "A)3  B)6  C)5", "a": "C"},
        {"q": "4) 3^2 = ?", "opts": "A)6  B)9  C)3", "a": "B"},
        {"q": "5) 10/2 = ?", "opts": "A)5  B)2  C)8", "a": "A"},
    ]

    if not payload.strip():
        text = "=== MINI QUIZ ===\n"
        for q in questions:
            text += f"{q['q']}\n{q['opts']}\n\n"
        text += "Відправ відповіді так: QUIZ|A,B,C,A,B"
        return text

    answers = payload.upper().replace(" ", "").split(",")
    if len(answers) != 5:
        return "Помилка: потрібно 5 відповідей (наприклад A,B,C,A,B)"

    score = 0
    for i in range(5):
        if answers[i] == questions[i]["a"]:
            score += 1

    return f"Твій результат: {score}/5"



# --- команди без сесії ---
COMMANDS = {
    "PAL": cmd_pal,
    "REV": cmd_rev,
    "WORDS": cmd_words,
    "VOWELS": cmd_vowels,
    "SQ": cmd_kvodrik,
    "QUIZ": cmd_quiz,
}

def parse_request_line(line: str) -> tuple[str, str]:
    line = line.strip()
    if " " not in line:
        return line.upper(), ""   # payload пустий
    command, payload = line.split(" ", 1)
    return command.strip().upper(), payload

def recv_line(conn: socket.socket, buffer: bytearray) -> str | None:
    while True:
        nl_index = buffer.find(b"\n")
        if nl_index != -1:
            raw_line = buffer[:nl_index]
            del buffer[:nl_index + 1]
            return raw_line.decode("utf-8", errors="replace").strip("\r")

        chunk = conn.recv(1024)
        if not chunk:
            return None
        buffer.extend(chunk)

def send_response(conn: socket.socket, status: str, payload: str) -> None:
    # нормальный протокол: одна строка = один ответ
    line = f"{status}|{payload}\n<<ENDOFTEXT>>\n"
    #print(f"<< {line}")
    conn.sendall(line.encode("utf-8"))

def handle_client(conn: socket.socket, addr) -> None:
    print(f"Connected by {addr}")
    buffer = bytearray()

    welcome_message = "\n" \
    "====== [QUIZ SERVER] ======\n" \
    "Welcome! \n" \
    "\n" \
    "Commands:\n" \
    "  REGISTER|name,age,email\n" \
    "  LOGIN|name\n" \
    "\n" \
    "=========\n"

    send_response(conn, "OK", welcome_message)


    # ВАЖНО: отдельная сессия на клиента
    session = LoginSystem()

    try:
        while True:
            line = recv_line(conn, buffer)
            if line is None:
                print(f"Client {addr} disconnected")
                return

            if line.strip() == "":
                send_response(conn, "ERR", "Empty request")
                continue

            try:
                command, payload = parse_request_line(line)

                if command == "QUIT":
                    send_response(conn, "OK", "Goodbye!")
                    return

                # --- команды сессии ---
                if command == "REGISTER":
                    # REGISTER|name,age,email
                    parts = [p.strip() for p in payload.split(",")]
                    if len(parts) != 3:
                        send_response(conn, "ERR", "REGISTER format: REGISTER|name,age,email")
                        continue
                    name, age_s, email = parts
                    resp = session.register(name, int(age_s), email)
                    send_response(conn, "OK", resp)
                    continue

                if command == "LOGIN":
                    # LOGIN|name
                    resp = session.login(payload)
                    send_response(conn, "OK", resp)
                    continue


                if command == "Q":
                    #питання, квіз
                    resp = session.as_question(payload)
                    send_response(conn, "питання:\n", resp)
                    continue

                if command == "A":
                    #відповідь на питання
                    resp = session.ans_question(payload)
                    send_response(conn, "A, done", resp)
                    continue

                if command == "ME":
                    # ME| (показ поточного)
                    if not session.current_user:
                        send_response(conn, "OK", "Ніхто не залогінений.")
                    else:
                        send_response(conn, "OK", session.show_user(session.current_user))
                    continue

                # --- обычные команды ---
                func = COMMANDS.get(command)
                if not func:
                    send_response(conn, "ERR", f"Unknown command: {command}")
                    continue

                result = func(payload)
                send_response(conn, "OK", result)

            except ValueError as e:
                send_response(conn, "ERR", str(e))
            except Exception as e:
                send_response(conn, "ERR", f"Server error: {type(e).__name__}: {e}")

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