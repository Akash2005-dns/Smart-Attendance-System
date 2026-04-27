from google_sheets import connect_sheet

sheet = connect_sheet()

sheet.append_row(["Akash", "2026-04-10", "12:00:00"])

print("✅ Test row added")