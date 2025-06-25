from database.init_db import db

class Section:

    def __init__(self, data):
        self.data = data
        self.name = data['name']
        self.description = data['description']
        self.counter = data['counter']
        data['users'] = None
        self.users = data['users']

        #self.user_data = user_data


    def isExist(self):
        section_data = db.collection("section").document(self.name).get()
        return section_data.exists

    def post(self):
        db.collection("section").document(self.name).set(self.data)

    def update(self, new_data):
        db.collection("section").document(self.name).set(new_data, merge=True)

    def entryUser(self, email):
        self.data['users'] += email
        db.collection("section").document(self.name).set(self.data, merge=True)
