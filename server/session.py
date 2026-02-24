# session.py

#from urllib import response

#from requests import session

#from quiz_server import send_response

class LoginSystem:
    def __init__(self):
        self.users = {}
        self.current_user = None
        self.asc_question = []
        self.current_q = -1
        self.score = 0
        self.dz_logged_in = False
        self.dz_started = True
        self.dz_idx = 0
        self.dz_answered = False
        self.dz_score = 0

    def register(self, name: str, age: int, email: str) -> str:
        name = name.strip()
        email = email.strip()

        if not name:
            return "Помилка: ім'я порожнє"

        if name in self.users:
            return "Ви вже зареєстровані!\n" + self.show_user(name)

        self.users[name] = {"age": age, "email": email}
        return "Реєстрація успішна!\n" + self.show_user(name)

    def login(self, name: str) -> str:
        name = name.strip()
        self.dz_logged_in = True
        self.asc_question = [
            {
            "id": 1,
            "question": "Яке число є простим?",
            "options": {
                "A": "21",
                "B": "29",
                "C": "39",
                "D": "51"
            },
            "correct_answer": "B"
            },
            {
            "id": 2,
            "question": "Скільки бітів у одному байті?",
            "options": {
                "A": "4",
                "B": "8",
                "C": "16",
                "D": "32"
            },
            "correct_answer": "B"
            },
            {
            "id": 3,
            "question": "Яка функція в Python використовується для виводу даних?",
            "options": {
                "A": "echo()",
                "B": "write()",
                "C": "print()",
                "D": "output()"
            },
            "correct_answer": "C"
            },
            {
            "id": 4,
            "question": "Хто є автором теорії відносності?",
            "options": {
                "A": "Ісаак Ньютон",
                "B": "Нікола Тесла",
                "C": "Альберт Ейнштейн",
                "D": "Галілео Галілей"
            },
            "correct_answer": "C"
            },
            {
            "id": 5,
            "question": "Яка столиця України?",
            "options": {
                "A": "Львів",
                "B": "Харків",
                "C": "Одеса",
                "D": "Київ"
            },
            "correct_answer": "D"
            },
            {
            "id": 6,
            "question": "Що повертає функція len() в Python?",
            "options": {
                "A": "Суму елементів",
                "B": "Довжину об’єкта",
                "C": "Тип змінної",
                "D": "Максимальне значення"
            },
            "correct_answer": "B"
            },
            {
            "id": 7,
            "question": "Яке з наведених чисел є ірраціональним?",
            "options": {
                "A": "0.5",
                "B": "√2",
                "C": "0.25",
                "D": "3/4"
            },
            "correct_answer": "B"
            }
            ]
        if name not in self.users:
            self.current_q = -1
            self.score = 0
            return "Вибач, але такого користувача немає. Спочатку REGISTER."

        self.current_user = name
        return "Привіт, " + name + "!\n" + self.show_user(name)

    def show_user(self, name: str) -> str:
        user = self.users.get(name)
        if not user:
            return "Немає такого користувача."

        return (
            "-(0_0)- Дані користувача -(0_0)-\n"
            f"Ім’я: {name}\n"
            f"Вік: {user['age']}\n"
            f"Email: {user['email']}\n"
            "------------------------"
            )
    def ask_question(self, payload: str = "", req_next: bool = False) -> str:
        if not self.current_user:
            return "Спочатку LOGIN|name (або REGISTER|name,age,email)."

        # якщо список питань ще не ініціалізовано — створимо тут (на всяк випадок)
        if not self.asc_question:
            return "Питання не завантажені. Зроби LOGIN ще раз (або перенеси питання в __init__)."

        if payload:
            raise ValueError("invalid arguments")
        if not self.dz_logged_in:
            raise ValueError("you must LOGIN first")
        if not self.dz_started:
            raise ValueError("quiz not started")



        if req_next and self.current_q >= 0 and not self.dz_answered:
            raise ValueError("you must answer current question first")
        
        if req_next:
            self.current_q += 1
            
        self.dz_answered = False

        if self.current_q >= len(self.asc_question):
            return f"Квіз завершено. Рахунок: {self.score}/{len(self.asc_question)}"

        q = self.asc_question[self.current_q]
        opts = "  ".join([f"{k}) {v}" for k, v in q["options"].items()])
        return f"{q['id']}) {q['question']}\n{opts}\n(Відповідай: A A або A B ...)"

    def start(self, payload: str) -> str:
        if payload:
            raise ValueError("START command does not take arguments")

        if not self.dz_logged_in:
            raise ValueError("you must LOGIN first")

        self.dz_started = True
        self.dz_idx = 0
        self.dz_answered = False
        self.dz_score = 0
        return "Quiz started! Use Q| to get the first question."

    def ans_question(self, payload: str) -> str:
        if not self.current_user:
            return "Спочатку LOGIN|name."
        if not self.dz_logged_in:
            raise ValueError("you must LOGIN first")
        if not self.dz_started:
            raise ValueError("quiz not started")

        if self.current_q < 0 or self.current_q >= len(self.asc_question):
            return "Спочатку запроси питання командою Q|"
        
        if self.dz_answered:
            raise ValueError("already answered")

        if not payload:
            raise ValueError("invalid arguments: answer is required")



        letter = payload.strip().upper()
        if letter not in ("A", "B", "C", "D"):
            raise ValueError("invalid arguments: answer must be A/B/C/D")

        ans = (payload or "").strip().upper()

        # дозволимо формат "A", "A)", "A) 29"
        if ans and ans[0] in "ABCD":
            ans = ans[0]
        else:
            return "Відповідь має бути A/B/C/D. Напр: A|B"

        q = self.asc_question[self.current_q]
        correct = q["correct_answer"].upper()
        


        self.dz_answered = True
        if ans == correct:
            self.score += 1
            return " Правильно!"
        return f" Неправильно. Правильна відповідь: {correct}"
    

    def get_score(self, payload: str) -> str:
        if not self.current_user:
            return "Спочатку LOGIN|name."
        if not self.dz_logged_in:
            raise ValueError("you must LOGIN first")
        if not self.dz_started:
            raise ValueError("quiz not started")

        return f"Ваш рахунок: {self.score}/{len(self.asc_question)}"
    
    def show_current_user(self) -> str:
        if not self.current_user:
            return "Ніхто не залогінений."
        return self.show_user(self.current_user)
    
    def is_logged_in(self) -> bool:
        return self.dz_logged_in
    
    def is_started(self) -> bool:
        return self.dz_started

    def process_command(self, cmd, payload):
        # REGISTER
        if cmd == "REGISTER":
            parts = [p.strip() for p in payload.split(",")] if payload else []
            if len(parts) != 3:
                raise ValueError("REGISTER format: REGISTER|name,age,email")

            name, age_s, email = parts
            try:
                age = int(age_s)
            except ValueError:
                raise ValueError("Age must be an integer")

            resp = self.register(name, age, email)
            return resp

        # LOGIN
        if cmd == "LOGIN":
            return self.login(payload)

        # ME
        if cmd == "ME":
            return self.show_current_user()

        # Якщо залогінений, але вікторина ще не стартувала — блокуємо “ігрові” команди
        if self.is_logged_in() and not self.is_started():
            if cmd in ("Q", "A", "NEXT", "SCORE"):
                raise ValueError("quiz not started (use START)")

        # START
        if cmd == "START":
            return self.start(payload)
            
        # Q
        if cmd == "Q":
            return self.ask_question(payload, req_next=False)

        # A (answer)
        if cmd == "A":
            return self.ans_question(payload)

        # NEXT
        if cmd == "NEXT":
            return self.ask_question(payload, req_next=True)

        # SCORE
        if cmd == "SCORE":
            return self.get_score(payload)

        # Додаткові команди — тільки після START і LOGIN
        raise ValueError(f"Unknown command: {cmd}")

    def welcome_message(self) -> str:
        return (
            "====== [QUIZ SERVER] ======\n"
            "Welcome!\n\n"
            "Commands:\n"
            "  REGISTER|name,age,email\n"
            "  LOGIN|name\n"
            "  ME|\n"
            "  START|\n"
            "  Q|\n"
            "  A|A  (або A|B/C/D)\n"
            "  NEXT|\n"
            "  SCORE|\n"
            "  QUIT|\n\n"
            "Extra (доступно ПІСЛЯ START): PAL, REV, WORDS, VOWELS, SQ, QUIZ\n"
            "===========================\n"
        ) 