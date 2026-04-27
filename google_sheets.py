import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def mark_attendance_google(name):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_file(
        r"C:\Users\SURIYA S\OneDrive\Desktop\SMART_ATTENDANCE_SYSTEM\credentials.json",
        scopes=scope
    )

    client = gspread.authorize(creds)
    sheet = client.open("Attendance").sheet1

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time_now = now.strftime("%H:%M:%S")

    # 🔥 GET ALL DATA FROM SHEET
    data = sheet.get_all_values()

    # 🔥 CHECK IF ALREADY MARKED
    for row in data:
        if len(row) >= 2:
            if row[0] == name and row[1] == date:
                print(f"⚠️ {name} already marked today (Google Sheets)")
                return

    # ✅ ADD NEW ROW
    sheet.append_row([name, date, time_now, "Present"])
    print("✅ Added to Google Sheets")