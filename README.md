# Smart-attendance-system

A Face Recognition Based Smart Attendance System built using Python, Flask, OpenCV, TensorFlow, and Google Sheets integration.

---

## Features

- Face detection and recognition
- Automatic attendance marking
- Student face registration
- Google Sheets attendance storage
- Web-based interface using Flask
- Real-time camera capture
- Face encoding generation

---

## Technologies Used

- Python
- Flask
- OpenCV
- TensorFlow
- face_recognition
- HTML/CSS
- Google Sheets API

---

## Project Structure

```bash
smart_attendance_system/
│
├── dataset/
├── encodings/
├── logs/
├── static/
├── templates/
│
├── app.py
├── capture_faces.py
├── encode_faces.py
├── recognize.py
├── google_sheets.py
├── requirements.txt
├── .gitignore
└── README.md


## Installation

### 1. Clone Repository

```bash
git clone https://github.com/Akash2005-dns/Smart-attendance-system.git
cd Smart-attendance-system
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv
```

---

### 3. Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux/macOS

```bash
source venv/bin/activate
```

---

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Project

```bash
python app.py
```

Open browser:

```text
http://127.0.0.1:5000
```

---

## How It Works

1. Capture student face images
2. Generate face encodings
3. Start attendance recognition
4. Attendance gets marked automatically
5. Data stored in Google Sheets

---

## Dataset and Encodings

- `dataset/` stores captured student face images
- `encodings/` stores generated facial encoding files

These folders may initially contain only `.gitkeep` placeholder files.

---
## Author

Akash

---

## License

This project is for educational purposes.
encodings/ stores generated facial encoding files

