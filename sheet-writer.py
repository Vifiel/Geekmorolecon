import firebase_admin
from firebase_admin import credentials, firestore
import gspread
from google.oauth2.service_account import Credentials
from gspread_formatting import set_frozen, CellFormat, format_cell_range
from googleapiclient.discovery import build

# === 1. Подключение к Firestore ===
firebase_cred = credentials.Certificate("registration-64a55-firebase-adminsdk-fbsvc-4ba297b537.json")
firebase_admin.initialize_app(firebase_cred)
db = firestore.client()

# === 2. Подключение к Google Sheets ===
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
gsheets_creds = Credentials.from_service_account_file("registration-64a55-5bc901cf90b6.json", scopes=SCOPES)
gc = gspread.authorize(gsheets_creds)

# === 3. Укажи название коллекции и ID таблицы ===
COLLECTION_NAME = "section"
SPREADSHEET_ID = "1yY-tYX4H5ZNsb0VldYwhGvrVq6KszTVacudQwL1osTY"

# === 4. Читаем данные из Firestore ===
docs = db.collection(COLLECTION_NAME).stream()

data = {}
for doc in docs:
    d = doc.to_dict()
    doc_name = d.get("name", f"document_{doc.id}")
    users = d.get("users", [])
    # Формируем список строк вида "name contact"
    data[doc_name] = [f"{u.get('name', '')} {u.get('contact', '')}".strip() for u in users]

# === 5. Приводим к табличному виду ===
# Определим максимальную длину списков (чтобы выровнять строки)
max_len = max(len(v) for v in data.values()) if data else 0
headers = list(data.keys())

# Заполняем таблицу
rows = []
for i in range(max_len):
    row = []
    for h_i, h in enumerate(headers):
        values = data[h]
        row.append(values[i] if i < len(values) else "")
    rows.append(row)

# === 6. Записываем в Google Sheets ===
sheet = gc.open_by_key(SPREADSHEET_ID).sheet1
sheet.clear()

sheet.append_row(headers)
if rows:
    sheet.append_rows(rows)

# Инициализируем API клиент
service = build("sheets", "v4", credentials=gsheets_creds)

# sheet.id — это ID листа внутри таблицы (получаешь через gspread)
sheet_id = sheet.id

# Формируем batchUpdate-запрос
body = {
    "requests": [
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS"
                }
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id},
                "cell": {
                    "userEnteredFormat": {
                        "wrapStrategy": "WRAP"
                    }
                },
                "fields": "userEnteredFormat.wrapStrategy"
            }
        }
    ]
}

# Отправляем запрос
service.spreadsheets().batchUpdate(
    spreadsheetId=SPREADSHEET_ID, body=body
).execute()
