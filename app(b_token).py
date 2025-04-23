import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from BearerMiddleware import BearerMiddleware
from models import db, Student

# Load environment variables
load_dotenv()
VALID_TOKEN = os.getenv("token")

# Initialize Flask App
app = Flask(__name__)
app.wsgi_app = BearerMiddleware(app.wsgi_app, VALID_TOKEN)  # Apply Middleware

# Configure Database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Routes
@app.route("/", methods=["GET"])
def index():
    user = request.environ.get("user")
    return jsonify(message=f"Welcome, {user['name']}!")

@app.route("/hello", methods=["GET"])
def hello():
    user = request.environ.get("user")
    return jsonify(message=f"Hello, {user['name']}! Hope you're doing great!")

@app.route("/goodbye", methods=["GET"])
def goodbye():
    user = request.environ.get("user")
    return jsonify(message=f"Goodbye, {user['name']}! Take care!")

@app.route('/students/')
def students():
    students = Student.query.all()
    return render_template('index.html', students=students)

@app.route('/<int:student_id>/')
def student(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('student.html', student=student)

@app.route('/<int:student_id>/edit/', methods=['GET', 'POST'])
def edit(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        student.firstname = request.form['firstname']
        student.lastname = request.form['lastname']
        student.email = request.form['email']
        student.age = int(request.form['age'])
        student.bio = request.form['bio']

        db.session.commit()
        return redirect(url_for('students'))

    return render_template('edit.html', student=student)

@app.route('/<int:student_id>/delete/', methods=['POST'])
def delete(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('students'))

@app.route('/create/', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        student = Student(
            firstname=request.form['firstname'],
            lastname=request.form['lastname'],
            email=request.form['email'],
            age=int(request.form['age']),
            bio=request.form['bio']
        )
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('students'))

    return render_template('create.html')

# Run App
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure database is created before running
    app.run(debug=True, port=8000)