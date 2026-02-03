from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()
from datetime import datetime

def fix_dates():
    for event in Event.query.all():
        if event.start_date and not isinstance(event.start_date, (datetime, date)):
            try:
                event.start_date = datetime.fromisoformat(str(event.start_date))
            except ValueError:
                event.start_date = None
        db.session.commit()
# ----------------------
# Event Model
# ----------------------
class Event(db.Model):
    __tablename__ = 'event'
    # __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)  # ✅ Correct
    end_date = db.Column(db.DateTime, nullable=False)    # ✅ Correct
    location = db.Column(db.String(120), nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    # status = db.Column(db.String(20), nullable=True)
    feedbacks = db.relationship('Feedback', backref='event', lazy=True)

    @property
    def current_status(self):
        today = datetime.utcnow().date()
        if self.start_date and self.end_date:
            if self.start_date.date() > today:
                return "Upcoming"
            elif self.start_date.date() <= today <= self.end_date.date():
                return "Ongoing"
            elif self.end_date.date() < today:
                return "Completed"
        return "Unknown"

    def __repr__(self):
        return f"<Event {self.name}>"
    # In your Event model, you could add property decorators to handle None values

# def current_status(self):
#         today = date.today()
#         if self.start_date > today:
#             return "Upcoming"
#         elif self.start_date <= today <= self.end_date:
#             return "Active"
#         elif self.end_date < today:
#             return "Completed"
#         return "Unknown"


# def __repr__(self):
#         return f"<Event {self.name}>"
# ----------------------
# Feedback Model
# ----------------------
class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    year = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text, nullable=False)

    anonymous = db.Column(db.Boolean, default=False)
    event_name = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

    def __repr__(self):
        return f"<Feedback {self.id} - {self.rating} stars>"
    
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
