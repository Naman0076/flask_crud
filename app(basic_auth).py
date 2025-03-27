import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.wrappers import Request, Response
import base64
from dotenv import load_dotenv
load_dotenv()
# Hardcoded Username & Password for Basic Auth
VALID_USERNAME = os.getenv("username")
VALID_PASSWORD = os.getenv("password")


# Basic Authentication Middleware
class BasicAuthMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Basic "):
            res = Response("Missing or invalid authentication", mimetype='text/plain', status=401)
            res.headers["WWW-Authenticate"] = 'Basic realm="Login Required"'
            return res(environ, start_response)

        # Extract username and password
        auth_decoded = base64.b64decode(auth_header.split(" ")[1]).decode("utf-8")
        username, password = auth_decoded.split(":", 1)

        # Validate Credentials
        if username != VALID_USERNAME or password != VALID_PASSWORD:
            res = Response("Unauthorized: Invalid credentials", mimetype='text/plain', status=401)
            return res(environ, start_response)

        # Store user info in request environment
        environ["user"] = {"name": username}
        return self.app(environ, start_response)

# Initialize Flask App
app = Flask(__name__)
app.wsgi_app = BasicAuthMiddleware(app.wsgi_app)  # Apply Middleware

# Configure Database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Student Model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    bio = db.Column(db.Text)

    def __repr__(self):
        return f'<Student {self.firstname}>'

# Routes
@app.route("/", methods=["GET"])
def index():
    user = request.environ.get("user")
    return redirect(url_for('students'))

@app.route("/hello", methods=["GET"])
def hello():
    user = request.environ.get("user")
    return jsonify(message=f"Hello, {user['name']}! Hope you're doing great!")

@app.route("/goodbye", methods=["GET"])
def goodbye():
    user = request.environ.get("user")
    return redirect(url_for('students'))
    
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
    app.run(debug=True, port=8000)
