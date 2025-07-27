from database.init_db import db
import uuid

class Section:

    def __init__(self, data):
        self.data = data
        self.name = data['name']
        self.description = data['description']
        self.places = data['places']
        self.date = data['date']
        self.time = data['time']
        self.counter = data['places']
        data['counter'] = self.counter
        
        self.master = data['master']
        self.masteClub = data['masterClub']
        self.system = data['system']
        self.id = str(uuid.uuid4())

        self.image = f"http://localhost:5000/image/games/{self.id}"

    def isExist(self):
        section_data = db.collection("section").document(self.id).get()
        return section_data.exists

    def post(self):
        data["image"] = self.image
        db.collection("section").document(self.id).set(self.data)

    def update(self, new_data):
        db.collection("section").document(self.id).set(new_data, merge=True)
