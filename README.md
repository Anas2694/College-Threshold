# 🎓 THRESHOLD — VTU Academic Tracker

A sleek, dark-themed academic tracker built for BMSCE/VTU students.  
Track marks, attendance, predict grades, manage bunks, and monitor SGPA/CGPA — all in one place.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **Marks Tracker** | Enter CIE, Quiz, AAT, Lab scores and get real-time internal marks out of 50 |
| 🎯 **Grade Predictor** | See exactly what SEE score you need for O / A+ / A / B+ / B / C |
| 📅 **Attendance Manager** | Track per-subject attendance with bunk budgets |
| 🚫 **Bunk Planner** | Smart cross-subject bunk planning + day simulator |
| 📈 **SGPA / CGPA** | Calculate current SGPA, track past semesters, run what-if scenarios |
| 📅 **Academic Calendar** | Full BMSCE Even Semester 2025-26 schedule with live countdowns (IST) |
| 👤 **Profile** | Name, department, current semester, photo |

---

## 🗂️ Project Structure

```
threshold/
├── app.py                  # Main entry point
├── requirements.txt
├── README.md
├── utils/
│   ├── __init__.py
│   ├── database.py         # All SQLite DB functions
│   ├── calculations.py     # Grade/marks/attendance math
│   ├── calendar_data.py    # BMSCE academic calendar data
│   └── styles.py           # Global CSS
└── pages/
    ├── __init__.py
    ├── dashboard.py        # Home dashboard
    ├── calendar_page.py    # Calendar view
    ├── sgpa_page.py        # SGPA / CGPA tracker
    ├── bunk_page.py        # Bunk planner
    ├── subject_detail.py   # Subject marks & attendance detail
    └── profile_page.py     # User profile
```

---

## 🚀 Getting Started

### Run locally

```bash
git clone https://github.com/YOUR-USERNAME/threshold.git
cd threshold
pip install -r requirements.txt
streamlit run app.py
```

### Run on Google Colab

```python
# Cell 1
!pip install streamlit pyngrok -q

# Cell 2 — upload your files or clone from GitHub
!git clone https://github.com/YOUR-USERNAME/threshold.git
%cd threshold

# Cell 3
!streamlit run app.py --server.port=8501 --server.headless=true &

# Cell 4
import time; time.sleep(10)
from pyngrok import ngrok
ngrok.set_auth_token("YOUR_NGROK_TOKEN")
url = ngrok.connect(8501, proto="http")
print("🚀 Live at:", url.public_url)
```

---

## 🏫 College

Built for **B.M.S. College of Engineering, Bengaluru-19**  
Autonomous Institute, Affiliated to VTU

---

## ⚠️ Disclaimer

This is a personal academic tool for educational purposes.  
Grade calculations follow BMSCE's internal assessment scheme — verify with your institution.

---

## 📄 License

MIT License — free to use and modify.
