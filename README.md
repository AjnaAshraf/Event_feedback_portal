
# EventFeedback System

A Flask-based web application for collecting and managing event feedback at Universal Engineering College.

## Features

- Modern, responsive UI with clean design
- Event listing with feedback collection
- Star rating system
- Admin dashboard for feedback management
- SQLite database for data storage
- Secure admin access

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Access the application at `http://localhost:5000`

## Admin Access

- URL: `/admin-uec`
- Default password: `admin123` (change this in production)

## Project Structure

```
eventfeedback/
├── app.py              # Main Flask application
├── requirements.txt    # Project dependencies
├── static/
│   └── style.css      # CSS styles
├── templates/
│   ├── base.html      # Base template
│   ├── index.html     # Home page
│   ├── feedback.html  # Feedback form
│   ├── thank_you.html # Thank you page
│   ├── admin_login.html    # Admin login
│   └── admin_dashboard.html # Admin dashboard
└── feedback.db        # SQLite database (created on first run)
```



---

## ⚙️ Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/AjnaAshraf/Event_feedback_portal.git
cd Event_feedback_portal

## Security Notes

- Change the `secret_key` in `app.py` before deployment
- Update the admin password in production
- Consider adding rate limiting for feedback submission
- Implement proper user authentication for admin access

## License

MIT License 

# Event_feedback_portal
Developed a Full Stack Event Feedback Portal using HTML, CSS, JavaScript, and Python. Admin can create and manage past, ongoing, and upcoming events. Students and faculty submit feedback for closed events, which the admin can view and analyze in real time.


---

## ✅ What to do now (VERY IMPORTANT)

1. **Replace your README.md content completely** with the above
2. Make sure there are **NO lines like**:
3. Save the file

---

## ✅ Finish Git process
Run:
```bash
git add README.md
git commit -m "Update README.md"
git push -u origin main
