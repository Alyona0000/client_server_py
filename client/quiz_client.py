
# =========================
# 1_TCP_Client.py (CLIENT)
# =========================
# TCP-клієнт для підключення до нашого сервера "TextTools".
#
# Клієнт:
#  - зчитує команду з консолі
#  - відправляє рядок на серQUITвер (закінчує '\n' щоб сервер знав, де кінець)
#  - читає відповідь сервера до '\n'
#  - друкує відповідь у форматі "OK: ..." або "ERR: ..."

import socket


def recv_line(conn: socket.socket, buffer: bytearray) -> str | None:
    """
    Читаємо один рядок до '\n' з TCP-потоку.

    Це та сама логіка, що і на сервері:
      - TCP = потік байтів
      - recv(1024) може повернути шматок повідомлення або кілька повідомлень
      - тому накопичуємо buffer і шукаємо '\n'
    """
    while True:
        nl_index = buffer.find(b"\n<<ENDOFTEXT>>")
        if nl_index != -1:
            raw_line = buffer[:nl_index]
            del buffer[:nl_index + 1]
            return raw_line.decode("utf-8", errors="replace")

        chunk = conn.recv(1024)
        if not chunk:
            return None  # сервер закрив з'єднання
        buffer.extend(chunk)

def main() -> None:
    HOST = "localhost"  # якщо сервер на тому ж комп'ютері
    PORT = 20002

    # Підказки користувачу (студенту)
    print("Commands: PAL, REV, WORDS, VOWELS,  SQ,  QUIZ")
    print("Format:   COMMAND|text")
    print("Example:  PAL|forof")
    print("Type 'quit' to exit.\n")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # connect() встановлює TCP-з'єднання з сервером
        s.connect((HOST, PORT))

        buffer = bytearray()  # буфер для recv_line()

        resp = recv_line(s, buffer)
        if resp is not None:
            print(resp)

        while True:
            user = input(">>> ").strip()

            # Локальна команда клієнта: вийти
            if user.lower() == "quit":
                # Домовленість: сервер розуміє команду QUIT
                s.sendall(b"QUIT|\n")

                # Прочитаємо відповідь сервера (якщо він її надішле)
                resp = recv_line(s, buffer)
                if resp is not None:
                    print(resp)
                break

            # Відправляємо введений рядок на сервер і ДОБАВЛЯЄМО '\n'
            # '\n' — це межа повідомлення в нашому протоколі.
            to_send = (user + "\n").encode("utf-8")
            s.sendall(to_send)

            # Читаємо рівно один рядок відповіді
            resp = recv_line(s, buffer)
            if resp is None:
                print("Server closed the connection.")
                break

            # Очікуємо формат: STATUS|payload
            if "|" in resp:
                status, payload = resp.split("|", 1)
                print(f"{status}: {payload}")
            else:
                # Якщо сервер відправив щось не за протоколом
                print(f"Invalid response: {resp}")


if __name__ == "__main__":
    main()