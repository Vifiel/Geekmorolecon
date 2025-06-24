import hashlib


class User:
    def __init__(self, email, password):
        self.password = hashlib.sha256(password.encode("utf-8")).hexdigest()
        self.email = email

class UserData(User):
    def __init__(self, data):
        self.data = data
        super().__init__(data["email"], data["password"])
        self.data["password"] = self.password
        self.data["isAdmin"] = False

    def post(self):
        db.collection("users").document(self.email).set(self.data)

