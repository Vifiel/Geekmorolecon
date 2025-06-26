from database.init_db import db
import pandas as pd
import os

def structureData(col):
    docs = db.collection(col).stream()

    data = []

    for doc in docs:
        doc_dict = doc.to_dict()
        doc_dict['__id__'] = doc.id  # добавим ID документа как поле
        data.append(doc_dict)
    return data


def import_data_to_file():
    output_dir = "static/files"
    os.makedirs(output_dir, exist_ok=True)

    columns = ["email",  "name", "sections"]
    # df = pd.DataFrame(data, columns=sorted(all_keys))
    df = pd.DataFrame(structureData('users'), columns=columns)

    columns = ["name", "description", "counter", "users"]
    # df = pd.DataFrame(data, columns=sorted(all_keys))
    ds = pd.DataFrame(structureData('section'), columns=columns)

    with pd.ExcelWriter('static/files/registredUsers.xlsx') as writer:
        df.to_excel(writer, index=False, sheet_name='Users')
        ds.to_excel(writer, index=False, sheet_name='Sections')


