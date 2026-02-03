from app import app, db
from models import Event, Feedback, ContactMessage

with app.app_context():
    Feedback.query.delete()
    ContactMessage.query.delete()
   
    db.session.commit()
    print("✅ All events, feedbacks, and contact messages deleted.")