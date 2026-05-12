from flask import Flask, render_template, request, redirect, session, Response
from flask_socketio import SocketIO
import gspread
from google.oauth2.service_account import Credentials
import time

app = Flask(__name__)
app.secret_key = "secret123"

socketio = SocketIO(app)

# 🔹 Google Sheets connection
def get_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=scope
    )

    return gspread.authorize(creds)

# 🔥 CACHE (to avoid API limit)
cached_users = []
cached_data = []
cached_class = []
last_users_time = 0
last_data_time = 0
last_class_time = 0

# 🔹 Get Users (Users tab)
def get_users():
    global cached_users, last_users_time

    if time.time() - last_users_time < 30:
        return cached_users

    client = get_client()
    sheet = client.open("Attendance").worksheet("Users")

    cached_users = sheet.get_all_records()
    last_users_time = time.time()

    return cached_users

# 🔹 Get Attendance (Sheet1)
def get_data():
    global cached_data, last_data_time

    if time.time() - last_data_time < 10:
        return cached_data

    client = get_client()
    sheet = client.open("Attendance").sheet1

    cached_data = sheet.get_all_records()
    last_data_time = time.time()

    return cached_data

# 🔹 Get Class List (Class tab)
def get_class_students():
    global cached_class, last_class_time

    if time.time() - last_class_time < 30:
        return cached_class

    client = get_client()
    try:
        class_sheet = client.open("Attendance").worksheet("Class")
        all_rows = class_sheet.get_all_values()
        if all_rows and len(all_rows) > 1:
            headers = [h.strip().lower() for h in all_rows[0]]
            name_col = next((i for i, h in enumerate(headers) if h in ("name", "names")), 0)
            cached_class = [row[name_col].strip() for row in all_rows[1:] if len(row) > name_col and row[name_col].strip()]
        else:
            cached_class = []
    except Exception:
        cached_class = []

    last_class_time = time.time()
    return cached_class

def get_full_class_attendance():
    raw_data = get_data()
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    # Read Class sheet raw (handles both 'Name' and 'Names' headers)
    try:
        client = get_client()
        class_sheet = client.open("Attendance").worksheet("Class")
        all_rows = class_sheet.get_all_values()
    except Exception:
        return raw_data

    if not all_rows or len(all_rows) < 2:
        return raw_data

    headers = [h.strip().lower() for h in all_rows[0]]
    name_col = next((i for i, h in enumerate(headers) if h in ("name", "names")), None)
    status_col = next((i for i, h in enumerate(headers) if h == "status"), None)

    if name_col is None or status_col is None:
        return raw_data

    # Build time lookup from Sheet1
    time_lookup = {str(r.get("Name", "")).strip(): r.get("Time", "-") for r in raw_data}

    full_attendance = []
    for row in all_rows[1:]:
        student_name = row[name_col].strip() if len(row) > name_col else ""
        if not student_name:
            continue
        status = row[status_col].strip() if len(row) > status_col else "Absent"
        if status not in ("Present", "Absent"):
            status = "Absent"
        full_attendance.append({
            "Name": student_name,
            "Date": today,
            "Time": time_lookup.get(student_name, "-"),
            "Status": status
        })
    return full_attendance

# 🔹 HOME
@app.route("/")
def home():
    return redirect("/login")

# 🔐 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    print("👉 LOGIN PAGE OPENED")

    if request.method == "POST":
        print("🔥 POST REQUEST HIT")

        username = request.form["username"].strip()
        password = request.form["password"].strip()

        print("INPUT:", username, password)

        users = get_users()
        print("USERS:", users)

        for user in users:
            clean_user = {k.strip().lower(): str(v).strip() for k, v in user.items()}

            username_db = clean_user.get("username", "")
            password_db = clean_user.get("password", "")
            role_db = clean_user.get("role", "").lower()

            print("DB:", username_db, password_db)

            if username_db == username and password_db == password:
                session["user"] = username
                session["role"] = role_db

                if role_db == "teacher":
                    return redirect("/teacher")
                else:
                    return redirect("/student")

        # 🔴 IMPORTANT: if login fails
        return "Invalid Login ❌"

    # 🔴 IMPORTANT: for GET request
    return render_template("login.html")

# 🔓 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# 👨‍🏫 TEACHER DASHBOARD
@app.route("/teacher")
def teacher_dashboard():
    if "user" not in session or session["role"] != "teacher":
        return redirect("/login")

    username = session["user"]
    
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    full_data = get_full_class_attendance()
    class_list = get_class_students()
    total_students = len(class_list) if class_list else len(full_data)
    total_present = sum(1 for row in full_data if row["Status"] == "Present")
    total_absent = max(0, total_students - total_present)
    percentage = round((total_present / total_students) * 100, 2) if total_students > 0 else 0

    return render_template("teacher.html", data=full_data, total=total_present, total_absent=total_absent, percentage=percentage, total_students=total_students, name=username, today=today)

# DATE FILTER
@app.route("/teacher/filter")
def teacher_filter():
    if "user" not in session or session["role"] != "teacher":
        return {"error": "Unauthorized"}, 401

    from datetime import datetime
    filter_date = request.args.get("date", "").strip()
    if not filter_date:
        filter_date = datetime.now().strftime("%Y-%m-%d")

    raw_data = get_data()
    class_list = get_class_students()

    present_on_date = {}
    for row in raw_data:
        if str(row.get("Date", "")).strip() == filter_date:
            name = str(row.get("Name", "")).strip()
            present_on_date[name] = row.get("Time", "-")

    result = []
    for student in class_list:
        if student in present_on_date:
            result.append({"Name": student, "Date": filter_date, "Time": present_on_date[student], "Status": "Present"})
        else:
            result.append({"Name": student, "Date": filter_date, "Time": "-", "Status": "Absent"})

    total_present = sum(1 for r in result if r["Status"] == "Present")
    total_absent = len(result) - total_present
    percentage = round((total_present / len(result)) * 100, 2) if result else 0

    return {
        "data": result,
        "total": total_present,
        "total_absent": total_absent,
        "percentage": percentage,
        "total_students": len(result)
    }

# DOWNLOAD CSV
@app.route("/download_csv")
def download_csv():
    if "user" not in session or session["role"] != "teacher":
        return redirect("/login")
        
    full_data = get_full_class_attendance()
    
    def generate():
        if not full_data:
            yield "Name,Date,Time,Status\n"
            return
            
        header = ["Name", "Date", "Time", "Status"]
        yield ",".join(header) + "\n"
        for row in full_data:
            yield ",".join(str(row.get(col, "")) for col in header) + "\n"
            
    return Response(generate(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=class_attendance.csv"})

# 👨‍🎓 STUDENT DASHBOARD
@app.route("/student")
def student_dashboard():
    if "user" not in session:
        return redirect("/login")

    username = session["user"]
    data = get_data()
    class_list = get_class_students()

    student_data = [row for row in data if str(row.get("Name", "")).strip() == username]
    total_present = len(student_data)

    # All unique dates class was conducted
    all_dates = sorted(set(str(row.get("Date", "")).strip() for row in data if str(row.get("Date", "")).strip()))
    present_dates = {str(row.get("Date", "")).strip() for row in student_data}

    # Build full record: present days + absent days
    full_records = []
    for d in all_dates:
        if d in present_dates:
            match = next(r for r in student_data if str(r.get("Date", "")).strip() == d)
            full_records.append({"Date": d, "Time": match.get("Time", "-"), "Status": "Present"})
        else:
            full_records.append({"Date": d, "Time": "-", "Status": "Absent"})

    total_classes = len(all_dates)
    total_absent = max(0, total_classes - total_present)
    percentage = round((total_present / total_classes) * 100, 2) if total_classes > 0 else 0

    return render_template(
        "student.html",
        data=full_records,
        total=total_present,
        total_absent=total_absent,
        total_classes=total_classes,
        percentage=percentage,
        name=username
    )

# 🔥 REAL-TIME UPDATES
def background_task():
    last_count = 0

    while True:
        raw_data = get_data()

        if len(raw_data) != last_count:
            last_count = len(raw_data)
            
            full_data = get_full_class_attendance()
            class_list = get_class_students()  # list of name strings
            total_students = len(class_list) if class_list else len(full_data)
            total_present = sum(1 for row in full_data if row["Status"] == "Present")
            total_absent = max(0, total_students - total_present)
            percentage = round((total_present / total_students) * 100, 2) if total_students > 0 else 0

            socketio.emit('update', {
                "data": full_data,
                "total": total_present,
                "total_absent": total_absent,
                "percentage": percentage,
                "total_students": total_students
            })

        time.sleep(10)  # avoid API limit

socketio.start_background_task(background_task)

# 🚀 RUN
if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)