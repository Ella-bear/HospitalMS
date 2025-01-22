from flask import Flask, send_from_directory, render_template, session, redirect, url_for, request, jsonify
from flask_restful import Resource, Api
from functools import wraps
from package.patient import Patients, Patient
from package.doctor import Doctors, Doctor
from package.appointment import Appointments, Appointment
from package.common import Common
from package.user import Auth, Users, UserResource, User
from package.prescription import Prescriptions, Prescription
import json
import sqlite3
import re

# Load config
with open('config.json') as data_file:
    config = json.load(data_file)

app = Flask(__name__, static_url_path='')
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key
api = Api(app)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Role required decorator
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] not in allowed_roles:
                return {'message': 'Unauthorized'}, 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# API routes
api.add_resource(Auth, '/login')
api.add_resource(Patients, '/patient')
api.add_resource(Patient, '/patient/<int:id>')
api.add_resource(Doctors, '/doctor')
api.add_resource(Doctor, '/doctor/<int:id>')
api.add_resource(Appointments, '/appointment')
api.add_resource(Appointment, '/appointment/<int:id>')
api.add_resource(Common, '/common')
api.add_resource(Prescriptions, '/prescription')
api.add_resource(Prescription, '/prescription/<int:id>')
api.add_resource(Users, '/users')
api.add_resource(UserResource, '/user/<int:id>')

# Web routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    if role == 'admin':
        return render_template('admin_dashboard.html')
    elif role == 'doctor':
        return render_template('doctor_dashboard.html')
    elif role == 'patient':
        return render_template('patient_dashboard.html')
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('user_type')
        
        # Basic validation
        if not all([username, email, password, user_type]):
            return jsonify({'message': 'All fields are required'}), 400
        
        # Email validation
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, email):
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Validate user type
        if user_type not in ['patient', 'doctor']:
            return jsonify({'message': 'Invalid user type'}), 400
        
        try:
            # Create user object
            user = User(username, password, user_type)
            
            conn = sqlite3.connect('hospital.db')
            cursor = conn.cursor()
            
            # Check if username exists
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                return jsonify({'message': 'Username already exists'}), 400
            
            # Insert the new user
            cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', (user.username, user.password, user.role))
            
            user_id = cursor.lastrowid
            
            # Create corresponding entry in patient or doctor table
            if user_type == 'patient':
                cursor.execute('''
                    INSERT INTO patients (user_id, name)
                    VALUES (?, ?)
                ''', (user_id, username))
            elif user_type == 'doctor':
                cursor.execute('''
                    INSERT INTO doctors (user_id, name)
                    VALUES (?, ?)
                ''', (user_id, username))
            
            conn.commit()
            return jsonify({'message': 'Account created successfully'}), 201
            
        except sqlite3.IntegrityError as e:
            print(f"Database integrity error: {str(e)}")
            return jsonify({'message': 'Username already exists'}), 400
        except Exception as e:
            print(f"Unexpected error during user creation: {str(e)}")
            return jsonify({'message': f'An error occurred while creating user: {str(e)}'}), 500
        finally:
            if conn:
                conn.close()

def get_db():
    db = sqlite3.connect('hospital.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.route('/patient/<int:id>/update', methods=['POST'])
def update_patient(id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
        
    data = request.get_json()
    # Update patient logic here
    return jsonify({'message': 'Profile updated successfully'})

if __name__ == '__main__':
    app.run(debug=True, host=config['host'], port=config['port'])