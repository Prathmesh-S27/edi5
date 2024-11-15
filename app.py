from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask application
app = Flask(__name__)
app.config.from_object('config') # Load configuration from config.py
# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db) 

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin' or 'student'

class Exam(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    age_min = db.Column(db.Integer, nullable=False)
    age_max = db.Column(db.Integer, nullable=False)
    education_level = db.Column(db.String(50), nullable=False)
    eligible_colleges = db.Column(db.Text, nullable=True)  # Comma-separated list of colleges
    mcqs = db.relationship('MCQ', backref='exam', lazy=True)

class ExamRegistration(db.Model):
    __tablename__ = 'exam_registrations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    college_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    aadhaar_number = db.Column(db.String(12), nullable=False)
    age = db.Column(db.Integer, nullable=False)

class MCQ(db.Model):
    __tablename__ = 'mcqs'
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)  # Foreign key to exams table
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
            session['user_id'] = user.id  # Add user_id to session
            flash('Login successful!', 'success')
            return redirect(url_for(f'{user.role}_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin':
        exams = Exam.query.all()
        return render_template('admin_dashboard.html', exams=exams)
    flash('Access unauthorized. Please log in as an admin.', 'danger')
    return redirect(url_for('login'))

@app.route('/admin/add_exam', methods=['GET', 'POST'])
def add_exam():
    if 'role' not in session or session['role'] != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        age_min = int(request.form['age_min'])
        age_max = int(request.form['age_max'])
        education_level = request.form['education_level']
        eligible_colleges = request.form['eligible_colleges']  # Comma-separated

        exam = Exam(
            name=name,
            description=description,
            age_min=age_min,
            age_max=age_max,
            education_level=education_level,
            eligible_colleges=eligible_colleges
        )
        db.session.add(exam)
        db.session.commit()
        flash('Exam added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_exam.html')

@app.route('/admin/set_mcqs/<int:exam_id>', methods=['GET', 'POST'])
def set_mcqs(exam_id):
    if 'role' not in session or session['role'] != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    exam = Exam.query.get_or_404(exam_id)

    if request.method == 'POST':
        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_answer = request.form['correct_answer']

        mcq = MCQ(
            exam_id=exam_id,
            question=question,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_answer=correct_answer
        )
        db.session.add(mcq)
        db.session.commit()
        flash('MCQ added successfully!', 'success')
        return redirect(url_for('set_mcqs', exam_id=exam_id))

    mcqs = MCQ.query.filter_by(exam_id=exam_id).all()
    return render_template('set_mcqs.html', exam=exam, mcqs=mcqs)

@app.route('/student_dashboard')
def student_dashboard():
    if 'role' in session and session['role'] == 'student':
        exams = Exam.query.all()
        return render_template('student_dashboard.html', exams=exams)
    flash('Access unauthorized. Please log in as a student.', 'danger')
    return redirect(url_for('login'))

@app.route('/register_exam/<int:exam_id>', methods=['GET', 'POST'])
def register_exam(exam_id):
    if 'role' not in session or session['role'] != 'student':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    exam = Exam.query.get_or_404(exam_id)

    if request.method == 'POST':
        name = request.form['name']
        college_name = request.form['college_name']
        address = request.form['address']
        aadhaar_number = request.form['aadhaar_number']
        age = int(request.form['age'])

        # Check eligibility
        if age < exam.age_min or age > exam.age_max:
            flash('You are not eligible for this exam due to age criteria.', 'danger')
            return redirect(url_for('register_exam', exam_id=exam_id))
        if exam.education_level != request.form['education_level']:
            flash('You are not eligible for this exam due to education criteria.', 'danger')
            return redirect(url_for('register_exam', exam_id=exam_id))
        if exam.eligible_colleges and college_name not in exam.eligible_colleges.split(','):
            flash('Your college is not eligible for this exam.', 'danger')
            return redirect(url_for('register_exam', exam_id=exam_id))

        registration = ExamRegistration(
            student_id=session['user_id'],
            exam_id=exam_id,
            name=name,
            college_name=college_name,
            address=address,
            aadhaar_number=aadhaar_number,
            age=age
        )
        db.session.add(registration)
        db.session.commit()
        flash('You have successfully registered for the exam!', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('register_exam.html', exam=exam)

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
