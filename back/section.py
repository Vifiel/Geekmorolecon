from database.init_db import db

class Section:

    def __init__(self, data):
        self.data = data
        self.name = data['name']
        self.description = data['description']
        self.places = data['places']
        self.date = data['date']
        self.time = data['time']
        self.counter = data['places']
        
        self.master = data['master']
        self.masteClub = data['masterClub']
        self.system = data['system']

        self.image = ""

    def isExist(self):
        section_data = db.collection("section").document(self.name).get()
        return section_data.exists

    def post(self):
        db.collection("section").document(self.name).set(self.data)

    def update(self, new_data):
        db.collection("section").document(self.name).set(new_data, merge=True)

    def entryUser(self, email):
        self.data['users'].append(email)
        db.collection("section").document(self.name).set(self.data, merge=True)
