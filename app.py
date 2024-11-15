from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask application
app = Flask(__name__)
app.config.from_object('config')  # Load configuration from config.py

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin' or 'student'

class MCQ(db.Model):
    __tablename__ = 'mcqs'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    option1 = db.Column(db.String(100), nullable=False)
    option2 = db.Column(db.String(100), nullable=False)
    option3 = db.Column(db.String(100), nullable=False)
    option4 = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.String(100), nullable=False)

# Routes
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Choose a different one.', 'warning')
            return redirect(url_for('register'))
        
        user = User(username=username, password=password, role=role)
        db.session.add(user)
        db.session.commit()

        flash(f'{role.capitalize()} registered successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for(f'{user.role}_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin':
        mcqs = MCQ.query.all()
        return render_template('admin_dashboard.html', mcqs=mcqs)
    flash('Access unauthorized. Please log in as an admin.', 'danger')
    return redirect(url_for('login'))

@app.route('/student_dashboard')
def student_dashboard():
    if 'role' in session and session['role'] == 'student':
        mcqs = MCQ.query.all()
        return render_template('exam.html', mcqs=mcqs)
    flash('Access unauthorized. Please log in as a student.', 'danger')
    return redirect(url_for('login'))

@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    if 'role' not in session or session['role'] != 'student':
        flash('Access unauthorized. Please log in as a student.', 'danger')
        return redirect(url_for('login'))

    # Scoring the submitted exam answers
    score = 0
    for key, value in request.form.items():
        mcq_id = int(key.split('_')[1])  # Extract MCQ ID from form field name
        mcq = MCQ.query.get(mcq_id)      # Fetch corresponding MCQ
        if mcq and mcq.correct_answer == value:
            score += 1

    flash(f'You scored {score} point(s)!', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Run the application
if __name__ == '__main__':
    db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
