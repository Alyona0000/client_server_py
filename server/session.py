# session.py

class LoginSystem:
    def __init__(self):
        self.users = {}
        self.current_user = None
        self.asc_question = []
        self.current_q = -1
        self.score = 0

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
    def as_question(self, payload: str = "") -> str:
        if not self.current_user:
            return "Спочатку LOGIN|name (або REGISTER|name,age,email)."

        # якщо список питань ще не ініціалізовано — створимо тут (на всяк випадок)
        if not self.asc_question:
            return "Питання не завантажені. Зроби LOGIN ще раз (або перенеси питання в __init__)."

        self.current_q += 1

        if self.current_q >= len(self.asc_question):
            return f"Квіз завершено. Рахунок: {self.score}/{len(self.asc_question)}"

        q = self.asc_question[self.current_q]
        opts = "  ".join([f"{k}) {v}" for k, v in q["options"].items()])
        return f"{q['id']}) {q['question']}\n{opts}\n(Відповідай: A A або A B ...)"


    def ans_question(self, payload: str) -> str:
        if not self.current_user:
            return "Спочатку LOGIN|name."

        if self.current_q < 0 or self.current_q >= len(self.asc_question):
            return "Спочатку запроси питання командою Q|"

        ans = (payload or "").strip().upper()

        # дозволимо формат "A", "A)", "A) 29"
        if ans and ans[0] in "ABCD":
            ans = ans[0]
        else:
            return "Відповідь має бути A/B/C/D. Напр: A|B"

        q = self.asc_question[self.current_q]
        correct = q["correct_answer"].upper()

        if ans == correct:
            self.score += 1
            return " Правильно!"
        return f" Неправильно. Правильна відповідь: {correct}"