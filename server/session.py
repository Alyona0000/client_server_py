class LoginSystem:
    def __init__(self):
        self.users = {}

    def register(self):
        name = input("-(0_0)-Введіть ім’я: ")

        if name in self.users:
            print("-(0_0)-Ви вже зареєстровані!")
            self.show_user(name)
            return

        age = int(input("-(0_0)-Введіть вік: "))
        email = input("-(0_0)-Введіть email: ")

        self.users[name] = {
            "age": age,
            "email": email
        }

        print("-(0_0)-Реєстрація успішна!")

    def login(self):
        name = input("-(0_0)-Введіть ім’я для входу: ")

        if name in self.users:
            print("-(0_0)-Ласкаво просимо,", name)
            self.show_user(name)
        else:
            print("-(0_0)-Користувача не знайдено.")

    def show_user(self, name):
        user = self.users[name]
        print("\n-(0_0)- Дані користувача -(0_0)-")
        print("Ім’я:", name)
        print("Вік:", user["age"])
        print("Email:", user["email"])
        print("------------------------")

    def menu(self):
        while True:
            print("\n1 - Реєстрація")
            print("2 - Вхід")
            print("3 - Вихід")

            choice = input("-(0_0)-Оберіть дію: ")

            if choice == "1":
                self.register()
            elif choice == "2":
                self.login()
            elif choice == "3":
                print("-(0_0)-Добре я спати!")
                break
            else:
                print("-(0_0)-Оберіть дію з меню.")


# запуск
system = LoginSystem()
system.menu()
