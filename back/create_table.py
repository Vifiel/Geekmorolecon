from database.init_db import db
import pandas as pd

def import_data_to_file():
    docs = db.collection("users").stream()

    data = []
    all_keys = set()

    for doc in docs:
        doc_dict = doc.to_dict()
        doc_dict['__id__'] = doc.id  # добавим ID документа как поле
        data.append(doc_dict)
        all_keys.update(doc_dict.keys())


    df = pd.DataFrame(data, columns=sorted(all_keys))

    df.to_excel("static/files/registredUsers.xlsx", index=False)

