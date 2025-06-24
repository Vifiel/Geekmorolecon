from database import init_db

db = init_db.db


class Section:

    def __init__(self, data):
        self.data = data
        self.name = data['name']
        self.description = data['description']
        self.counter = data['counter']



    def post(self):

        db.collection("section").document(self.name).set(self.data)
