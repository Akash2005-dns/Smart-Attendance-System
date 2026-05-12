import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def get_sheet_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(
        r"C:\Users\SURIYA S\OneDrive\Desktop\SMART_ATTENDANCE_SYSTEM\credentials.json",
        scopes=scope
    )
    return gspread.authorize(creds)

def update_class_sheet(name):
    """Mark student as Present in Class sheet. Supports 'Name' or 'Names' header."""
    client = get_sheet_client()
    try:
        class_sheet = client.open("Attendance").worksheet("Class")
    except gspread.exceptions.WorksheetNotFound:
        print("⚠️ Class sheet not found")
        return

    all_rows = class_sheet.get_all_values()
    if not all_rows or len(all_rows) < 2:
        print("⚠️ Class sheet is empty")
        return

    headers = [h.strip().lower() for h in all_rows[0]]
    print(f"📋 Class sheet headers: {all_rows[0]}")

    # Accept both 'name' and 'names'
    name_col = next((i for i, h in enumerate(headers) if h in ("name", "names")), None)
    status_col = next((i for i, h in enumerate(headers) if h == "status"), None)
    date_col = next((i for i, h in enumerate(headers) if h == "date"), None)

    if name_col is None or status_col is None:
        print(f"⚠️ Need 'Name'/'Names' and 'Status' columns. Found: {all_rows[0]}")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    student_rows = all_rows[1:]

    # Reset all students to Absent if date changed (new day) or status is blank
    for i, row in enumerate(student_rows):
        row_num = i + 2
        student_name = row[name_col].strip() if len(row) > name_col else ""
        if not student_name:
            continue
        current_date = row[date_col].strip() if date_col is not None and len(row) > date_col else ""
        current_status = row[status_col].strip() if len(row) > status_col else ""
        # Reset if new day OR blank
        if current_date != today or current_status == "":
            class_sheet.update_cell(row_num, status_col + 1, "Absent")
            if date_col is not None:
                class_sheet.update_cell(row_num, date_col + 1, today)

    # Mark recognized student as Present
    found = False
    for i, row in enumerate(student_rows):
        row_num = i + 2
        student_name = row[name_col].strip() if len(row) > name_col else ""
        if student_name.lower() == name.lower():
            class_sheet.update_cell(row_num, status_col + 1, "Present")
            if date_col is not None:
                class_sheet.update_cell(row_num, date_col + 1, today)
            print(f"✅ Class sheet: {name} → Present ({today})")
            found = True
            break

    if not found:
        print(f"⚠️ '{name}' not found in Class sheet")

def mark_attendance_google(name):
    client = get_sheet_client()
    sheet = client.open("Attendance").sheet1

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time_now = now.strftime("%H:%M:%S")

    data = sheet.get_all_values()

    for row in data:
        if len(row) >= 2:
            if row[0] == name and row[1] == date:
                print(f"⚠️ {name} already marked today (Google Sheets)")
                return

    sheet.append_row([name, date, time_now, "Present"])
    print("✅ Added to Google Sheets")
