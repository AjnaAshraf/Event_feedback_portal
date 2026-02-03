from flask import Flask,session, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from sqlalchemy import func

import sqlite3
import os
from statistics import mean
from flask import Flask,render_template, request, redirect, url_for
from models import db, Event, Feedback,ContactMessage

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///feedback.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ✅ Link app with db
db.init_app(app)
with app.app_context():
    db.create_all()
app.secret_key = 'your-secret-key-here'
app.static_folder = 'static'
migrate = Migrate(app, db)

# Database initialization
def init_db():
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    # Create feedback table with new fields
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comments TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            name TEXT NOT NULL DEFAULT '',
            email TEXT NOT NULL DEFAULT '',
            department TEXT NOT NULL DEFAULT '',
            year TEXT DEFAULT NULL,
            designation TEXT DEFAULT NULL,
            role TEXT NOT NULL DEFAULT 'student'
        )
    ''')
    # Check if we need to add new columns
    c.execute("PRAGMA table_info(feedback)")
    columns = [col[1] for col in c.fetchall()]
    
    # Add missing columns with default values
    if 'name' not in columns:
        c.execute('ALTER TABLE feedback ADD COLUMN name TEXT NOT NULL DEFAULT ""')
    if 'email' not in columns:
        c.execute('ALTER TABLE feedback ADD COLUMN email TEXT NOT NULL DEFAULT ""')
    if 'department' not in columns:
        c.execute('ALTER TABLE feedback ADD COLUMN department TEXT NOT NULL DEFAULT ""')
    if 'year' not in columns:
        c.execute('ALTER TABLE feedback ADD COLUMN year TEXT DEFAULT NULL')
    if 'designation' not in columns:
        c.execute('ALTER TABLE feedback ADD COLUMN designation TEXT DEFAULT NULL')
    if 'role' not in columns:
        c.execute('ALTER TABLE feedback ADD COLUMN role TEXT NOT NULL DEFAULT "student"')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Sample events data - ONLY 5 EVENTS
SAMPLE_EVENTS = [
    {
        "name": "UEC TechFest",
        "description": "UEC's TechFest brings together innovation, creativity, and technical excellence with competitions, workshops, and tech talks.",
        "images": ["images/techfest.jpg", "images/tech2.jpg", "images/tech3.jpg", "images/tech4.jpg", "images/techfest3.jpg"]
    },
    {
        "name": "Workshop on Building the Nation",
        "description": "A session by Mr. V. Suresh on sustainable development and nation-building strategies for engineers.",
        "images": ["images/workshop.jpg"]
    },
    {
        "name": "Cultural Fest",
        "description": "A vibrant festival showcasing talent in music, dance, drama, and fashion from across the campus.",
        "images": ["images/കല എന്നത് കരവിരുത് മാത്രമല്ല. അത് കലാകാരനായിട്ടുള്ള അനുഭവങ്ങളുടെ പ്രകടനമാണ്....ഇവിടം അത് അ.jpg", "images/തകൃതി🌼...#onam #maveli #onamcelebration.jpg", "images/collage day 1.jpg","images/collage day vidhu.webp","images/cultural.png","images/onam thakrithi.png", "images/mechonam.png","images/🔥💥.jpg"]
    },
    {
        "name": "Internship Fair",
        "description": "Partnered with over 20 companies, this event helps students secure summer internships through live interaction and interviews.",
        "images": ["images/internship ceo.webp", "images/main-lab-scaled.jpg"]
    },
    {
        "name": "UEC Annual Sports Meet",
        "description": "Students from all branches participated in interdepartmental sports events. The meet celebrated teamwork, talent, and healthy competition.",
        "images": ["images/sportsssss.jpg", "images/khelo1.png", "images/khelo 2.jpg"]
    },
]

def get_event_stats():
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    
    allowed_events = [event['name'] for event in SAMPLE_EVENTS]
    placeholders = ','.join(['?'] * len(allowed_events))
    query = f'''
        SELECT event, 
               COUNT(*) as count,
               AVG(rating) as avg_rating
        FROM feedback 
        WHERE event IN ({placeholders})
        GROUP BY event
        ORDER BY count DESC
    '''
    
    c.execute(query, allowed_events)
    
    events = []
    for row in c.fetchall():
        events.append({
            'name': row[0],
            'feedback_count': row[1],
            'avg_rating': round(row[2], 1) if row[2] else 0,
            'last_feedback': 'Recently'  # This would be fetched from the database in a real app
        })
    
    conn.close()
    return events

@app.route('/')
def index():
    return render_template('index.html', events=SAMPLE_EVENTS)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/events')
def events():
    events = Event.query.order_by(Event.start_date.desc()).all()
    return render_template('events.html', events=events)



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        if name and email and message:
            new_message = ContactMessage(name=name, email=email, message=message)
            db.session.add(new_message)
            db.session.commit()
            flash('Message sent successfully.', 'success')
        else:
            flash('All fields are required.', 'danger')

        return redirect(url_for('contact'))

    return render_template('contact.html')



@app.route('/eventlist')
def eventlist():
    events = Event.query.order_by(Event.start_date).all()
    return render_template('eventlist.html', events=events)


  # or allow admin to choose
@app.route('/create-event', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        location = request.form['location']
        # status = request.form.get('status')
        start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%d").date()
        end_date = datetime.strptime(request.form['end_date'], "%Y-%m-%d").date()

        # Handle uploaded image
        image = request.files.get('image')
        if image and image.filename != '':
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            image_url = '/' + image_path.replace('\\', '/')  # Web-friendly URL
        else:
            image_url = '/static/default.jpg'

        # Create and save the event
        new_event = Event(
            name=name,
            category=category,
            start_date=start_date,
            end_date=end_date,
            location=location,
            # status=status,
            image_url=image_url
        )
        db.session.add(new_event)
        db.session.commit()

        return redirect(url_for('eventlist'))

    # Show form on GET request
    return render_template('create_event.html')

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    return render_template('edit_event.html', event=event)


@app.route('/update-event/<int:event_id>', methods=['POST'])
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    event.name = request.form['name']
    event.category = request.form['category']
    event.location = request.form['location']
   
   # event.current_status = request.form.get('status')
    event.start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%d").date()
    event.end_date = datetime.strptime(request.form['end_date'], "%Y-%m-%d").date()

    image = request.files.get('image')
    if image and image.filename != '':
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        event.image_url = '/' + image_path.replace('\\', '/')

    db.session.commit()
    return redirect(url_for('eventlist'))

@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('eventlist'))

@app.route('/feedback/<int:event_id>', methods=['GET', 'POST'])
def feedback(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        name = request.form['name']
        rating = int(request.form['rating'])
        comments = request.form['comments']
        anonymous = 'anonymous' in request.form

        feedback = Feedback(
            name=name,
            rating=rating,
            comments=comments,
            anonymous=anonymous,
            event_id=event.id  # ✅ save feedback linked to event
        )

        db.session.add(feedback)
        db.session.commit()
        return redirect(url_for('events'))

    return render_template('feedback.html', event=event)

from models import Feedback, db

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    event_name = request.form.get('event')
    rating = int(request.form.get('rating'))
    comments = request.form.get('comments')
    name = request.form.get('name')
    email = request.form.get('email')
    department = request.form.get('department')
    role = request.form.get('role')
    year = request.form.get('year')
    designation = request.form.get('designation')

    # Determine event_id if you store feedback linked to an event
    event = Event.query.filter_by(name=event_name).first()
    event_id = event.id if event else None

    feedback = Feedback(
        name=name,
        email=email,
        department=department,
        year=year,
        rating=rating,
        comments=comments,
        anonymous=False,
        event_id=event_id,
        event_name=event_name
    )

    db.session.add(feedback)
    db.session.commit()

    return redirect(url_for('thank_you'))

@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/admin-uec', methods=['GET', 'POST'])
def admin_login():
    if 'admin_logged_in' in session:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check credentials
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('admin_login.html')

# @app.route('/admin-dashboard')
# def admin_dashboard():
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('admin_login'))
    
#     events = Event.query.order_by(Event.start_date).all()

#     return render_template('admin_dashboard.html', events=events)
# @app.route('/admin-dashboard')
# def admin_dashboard():
#     try:
#         events = Event.query.order_by(Event.start_date).all()
#     except Exception as e:
#         print(f"Error loading events: {str(e)}")
#         events = []
#     return render_template('admin_dashboard.html', events=events)
# Change this logout route
# Add these imports at the top
from sqlalchemy import func

# Update the admin_dashboard route
@app.route('/admin-dashboard')
def admin_dashboard():
    search_query = request.args.get('search', '').strip()

    if search_query:
        events = Event.query.filter(Event.name.ilike(f"%{search_query}%")).all()
    else:
        events = Event.query.order_by(Event.start_date.desc()).all()
    
    # Calculate event statistics
    for event in events:
        ratings = [fb.rating for fb in event.feedbacks]
        event.avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Calculate total feedback
    total_feedback = sum(len(event.feedbacks) for event in events)
    
    # Calculate overall average rating
    all_ratings = [fb.rating for event in events for fb in event.feedbacks]
    avg_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 0
    
    return render_template('admin_dashboard.html', 
                          events=events,
                          total_feedback=total_feedback,
                          avg_rating=avg_rating)

@app.route('/admin-uec/event/<event_name>')
def event_feedback(event_name):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Only allow defined events
    if event_name not in [event['name'] for event in SAMPLE_EVENTS]:
        flash('Event not found', 'error')
        return redirect(url_for('admin_dashboard'))
    
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    
    # Get feedback for specific event with new fields
    c.execute('''
        SELECT id, rating, comments, submitted_at, name, email, department, role, year, designation
        FROM feedback
        WHERE event = ?
        ORDER BY submitted_at DESC
    ''', (event_name,))
    
    feedbacks = []
    for row in c.fetchall():
        try:
            timestamp = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
            formatted_date = timestamp.strftime('%B %d, %Y - %I:%M %p')
        except:
            formatted_date = row[3]
        
        feedbacks.append({
            'id': row[0],
            'rating': row[1],
            'comments': row[2],
            'submitted_at': formatted_date,
            'name': row[4],
            'email': row[5],
            'department': row[6],
            'role': row[7],
            'year': row[8],
            'designation': row[9]
        })
    
    # Calculate average rating
    c.execute('SELECT AVG(rating) FROM feedback WHERE event = ?', (event_name,))
    avg_rating = c.fetchone()[0] or 0
    avg_rating = round(avg_rating, 1)
    
    conn.close()
    
    return render_template('event_feedback.html', 
                         event_name=event_name,
                         feedbacks=feedbacks,
                         avg_rating=avg_rating)

@app.route('/logout')
def logout():
    # Clear session or any login-related cookie if you use one
    session.clear()  # If you're using Flask session
    return redirect(url_for('admin_login'))  # or wherever your login page is

@app.route('/admin/messages')
def admin_messages():
    messages = ContactMessage.query.order_by(ContactMessage.timestamp.desc()).all()
    return render_template('admin_messages.html', messages=messages)

if __name__ == '__main__':
    app.run(debug=True)