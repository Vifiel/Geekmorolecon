import hashlib
from flask_login import UserMixin, AnonymousUserMixin
from database.init_db import db

class User(UserMixin):
    def __init__(self, email, password, is_admin=False):
        # self.password = hashlib.sha256(password.encode("utf-8")).hexdigest()
        self.password = password
        self.email = email
        self.isAdmin = is_admin

    def get_id(self):
        return self.email

    @staticmethod
    def get(email):
        # Получаем пользователя по email (который является ID)
        user_ref = db.collection('users').document(email)
        user_data = user_ref.get()

        if user_data.exists:
            user_dict = user_data.to_dict() or {}
            return User(
                email=email,
                contact=contact,
                password=user_dict.get('password'),
                is_admin=user_dict.get("isAdmin", False)
            )
        return None

class UserData(User):
    def __init__(self, data):
        self.data = data
        super().__init__(data["email"], data["password"])
        self.data["password"] = self.password
        self.data["isAdmin"] = False

    def post(self):
        db.collection("users").document(self.email).set(self.data)

