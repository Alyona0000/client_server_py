# session.py

class LoginSystem:
    def __init__(self):
        self.users = {}
        self.current_user = None

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