
import socket
import re

# Регулярний вираз для “розділювачів” (пробіли + пунктуація).
# Використовуємо для нормалізації в задачі PAL (паліндром).
_SEPARATORS_RE = re.compile(r"""[ \t!?.,+:;"'()\-]+""")


def normalize_text(s: str) -> str:
    """
    Нормалізуємо рядок для перевірки паліндрома:
      1) прибираємо пробіли та розділові знаки
      2) приводимо до нижнього регістру

    Приклад:
      "А роза упала..." -> "арозаупаланалапуазора"
    """
    s = _SEPARATORS_RE.sub("", s)  # замінюємо всі розділювачі на "" (видаляємо)
    return s.lower()


def cmd_pal(payload: str) -> str:
    """
    Команда PAL: перевірка паліндрома.
    Повертаємо текст "1" якщо паліндром, і "0" якщо ні.

    t[::-1] — це “перевернута” версія рядка t.
    """
    t = normalize_text(payload)
    return "1" if t == t[::-1] else "0"


def cmd_rev(payload: str) -> str:
    """
    Команда REV: просто повертає рядок навпаки.
    """
    return payload[::-1]


def cmd_words(payload: str) -> str:
    """
    Команда WORDS: рахуємо кількість слів.
    payload.split() без аргументів:
      - ігнорує зайві пробіли
      - рахує “слова” як блоки між пробілами/табами/переносами
    """
    words = payload.split()
    return str(len(words))


def cmd_vowels(payload: str) -> str:
    """
    Команда VOWELS: рахуємо кількість голосних у тексті.
    Підтримуємо англійські + українські голосні.
    """
    vowels = set("aeiouyAEIOUY" "аеиіоуяюєїАЕИІОУЯЮЄЇ")
    return str(sum(1 for ch in payload if ch in vowels))

#################################################################################

def cmd_kvodrik(payload: float) -> float:
    """
    возводить число в квадрат
    """
    kvodrik = int(payload)*int(payload)
    return kvodrik

######################################################################################
#####################################################################################
#  як на сервері реалізувати квіз тест 



def cmd_quiz(payload: str) -> str:
    """
    Команда QUIZ.
    payload має вигляд: A,C,B,A,C
    Повертає результат тесту.
    """
    questions = [
        {
            "q": "1) 2+3 = ?",
            "opts": "A)2  B)3  C)5",
            "a": "C"
        },
        {
            "q": "2) 5*2 = ?",
            "opts": "A)7  B)10  C)12",
            "a": "B"
        },
        {
            "q": "3) 9-4 = ?",
            "opts": "A)3  B)6  C)5",
            "a": "C"
        },
        {
            "q": "4) 3^2 = ?",
            "opts": "A)6  B)9  C)3",
            "a": "B"
        },
        {
            "q": "5) 10/2 = ?",
            "opts": "A)5  B)2  C)8",
            "a": "A"
        }
    ]

    # Якщо payload пустий — просто показуємо тест
    if not payload.strip():
        text = "=== MINI QUIZ ===\n"
        for q in questions:
            text += f"{q['q']}\n{q['opts']}\n\n"
        text += "Відправ відповіді так: QUIZ|A,B,C,A,B"
        return text

    # Інакше перевіряємо відповіді
    answers = payload.upper().replace(" ", "").split(",")

    if len(answers) != 5:
        return "Помилка: потрібно 5 відповідей (наприклад A,B,C,A,B)"

    score = 0
    for i in range(5):
        if answers[i] == questions[i]["a"]:
            score += 1

    return f"Твій результат: {score}/5"




############################################################################################

COMMANDS = {
    "PAL": cmd_pal,
    "REV": cmd_rev,
    "WORDS": cmd_words,
    "VOWELS": cmd_vowels,
    "SQ": cmd_kvodrik,
    "QUIZ": cmd_quiz,
}

def parse_request_line(line: str) -> tuple[str, str]:
    """
    Розбираємо рядок запиту формату COMMAND|payload.

    Повертаємо (command, payload).
    Якщо '|' немає — формат неправильний, кидаємо ValueError.
    """
    if "|" not in line:
        raise ValueError("Expected 'COMMAND|payload' format")

    # split("|", 1) — розділяємо тільки 1 раз.
    # Це важливо: payload може містити символи '|' (тоді ми не зламаємось).
    command, payload = line.split("|", 1)

    # Команду чистимо (strip) і робимо upper, щоб "pal" і "PAL" працювали однаково.
    command = command.strip().upper()
    return command, payload


def recv_line(conn: socket.socket, buffer: bytearray) -> str | None:
    """
    Отримуємо ОДИН рядок до '\n' із TCP-потоку.

    Чому так складно, а не просто conn.recv(1024)?
      - TCP не гарантує, що один recv = одне “повідомлення”.
      - Ми можемо отримати:
           * половину повідомлення,
           * або одразу 2 повідомлення разом.
      - Тому ми накопичуємо байти у buffer і “дістаємо” рядок, коли побачили '\n'.

    Повертаємо:
      - str (рядок без '\n') якщо успішно прочитали
      - None якщо клієнт закрив з’єднання (recv повернув b'')
    """
    while True:
        # Шукаємо '\n' в буфері
        nl_index = buffer.find(b"\n")
        if nl_index != -1:
            # Беремо все до '\n' (сам '\n' не включаємо)
            raw_line = buffer[:nl_index]

            # Видаляємо з буфера використану частину + сам '\n'
            del buffer[:nl_index + 1]

            # Перетворюємо bytes -> str (UTF-8)
            # errors="replace" означає: якщо прийшли “биті” байти, не падати, а підставити �
            return raw_line.decode("utf-8", errors="replace")

        # Якщо '\n' ще нема — дочитуємо наступний шматок з мережі
        chunk = conn.recv(1024)

        # Якщо chunk порожній — клієнт закрив з’єднання
        if not chunk:
            return None

        buffer.extend(chunk)


def send_response(conn: socket.socket, status: str, payload: str) -> None:
    """
    Відправляємо відповідь клієнту у форматі:
        STATUS|payload\n
    де STATUS = "OK" або "ERR".
    """
    line = f"{status}|{payload}\n<<ENDOFTEXT>>"
    print(f"Sending response: {line.strip()}")
    conn.sendall(line.encode("utf-8"))  # sendall гарантує відправку всіх байтів


def handle_client(conn: socket.socket, addr) -> None:
    """
    Обробляємо одного клієнта:
      - читаємо запити (рядки)
      - розбираємо команду + параметри
      - викликаємо відповідну функцію
      - відправляємо відповідь
    """
    print(f"Connected by {addr}")
    buffer = bytearray()  # тут накопичуємо байти, які прийшли по TCP
    session = jkljlkl
    try:
        while True:
            line = recv_line(conn, buffer)
            if line is None:
                print(f"Client {addr} disconnected")
                return

            # Іноді текстові протоколи використовують \r\n (Windows style),
            # тому прибираємо \r якщо він є.
            line = line.strip("\r")

            # Порожній рядок — трактуємо як помилку (можна було б ігнорувати/quit).
            if line == "":

                send_response(conn, "ERR", "Empty request535")
                continue

            try:
                # Розбираємо команду
                command, payload = parse_request_line(line)

                # Спеціальна команда для завершення сесії
                if command == "QUIT":
                    send_response(conn, "OK", "Goodbye!")
                    return

                # Знаходимо функцію по команді
                func = COMMANDS.get(command)
                if func is None:
                    send_response(conn, "ERR", f"Unknown command: {command}")
                    continue

                # Виконуємо команду та відправляємо результат
                result = func(payload)
                send_response(conn, "OK", result)

            except ValueError as e:
                # Помилки формату протоколу (наприклад, нема '|')
                send_response(conn, "ERR", str(e))

            except Exception as e:
                # “Захист”: сервер не повинен падати від випадкової помилки.
                # Студентам: краще логувати повний traceback у реальних проектах.
                send_response(conn, "ERR", f"Server error: {type(e).__name__}")

    finally:
        # Закриваємо сокет з'єднання з клієнтом
        conn.close()


def main() -> None:
    """
    Точка входу: створюємо серверний сокет, биндимось на порт,
    і в циклі приймаємо клієнтів.
    """
    HOST = ""       # "" означає: слухати на всіх інтерфейсах (0.0.0.0)
    PORT = 20002    # порт сервера (клієнт має підключатися до цього ж порту)

    # AF_INET -> IPv4, SOCK_STREAM -> TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Дозволяє швидко перезапустити сервер без "Address already in use"
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Прив'язуємо сокет до (HOST, PORT)
        s.bind((HOST, PORT))

        # Починаємо "слухати" вхідні підключення.
        # 5 — це “черга очікування”: скільки клієнтів може чекати accept().
        s.listen(5)
        print(f"Server listening on port {PORT} and host {HOST!r}")

        # Нескінченний цикл: сервер працює постійно
        while True:
            # accept() блокує виконання, поки не прийде клієнт.
            conn, addr = s.accept()

            # Для простоти: обслуговуємо клієнта одразу тут.
            # (Мінус: поки один клієнт працює — інші чекають.)
            handle_client(conn, addr)


if __name__ == "__main__":
    main()