import sqlite3
import hashlib
import os
from datetime import datetime

def hash_password(password):
    # Create a random salt
    salt = os.urandom(32)
    # Combine password and salt, then hash
    hash_obj = hashlib.sha256(salt + password.encode('utf-8'))
    # Return salt and hash combined
    return salt.hex() + hash_obj.hexdigest()

def init_db():
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS appointments')
    cursor.execute('DROP TABLE IF EXISTS doctors')
    cursor.execute('DROP TABLE IF EXISTS patients')
    cursor.execute('DROP TABLE IF EXISTS users')

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')

    # Add default users
    default_users = [
        ('admin', 'admin123', 'admin'),
        ('doctor1', 'doctor123', 'doctor'),
        ('doctor2', 'doctor123', 'doctor'),
        ('patient1', 'patient123', 'patient'),
        ('patient2', 'patient123', 'patient')
    ]

    for username, password, role in default_users:
        cursor.execute('''
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
        ''', (username, hash_password(password), role))

    # Create doctors table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT NOT NULL,
        specialization TEXT,
        phone TEXT,
        address TEXT,
        schedule TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Add sample doctors
    sample_doctors = [
        (2, 'Dr. John Smith', 'Cardiologist', '+1234567890', '123 Medical Center', 'Mon-Fri 9AM-5PM'),
        (3, 'Dr. Sarah Johnson', 'Pediatrician', '+1234567891', '456 Health Plaza', 'Mon-Fri 8AM-4PM'),
        (4, 'Dr. Michael Brown', 'Neurologist', '+1234567892', '789 Brain Center', 'Mon-Thu 10AM-6PM'),
        (5, 'Dr. Emily Davis', 'Dermatologist', '+1234567893', '321 Skin Clinic', 'Tue-Sat 9AM-5PM')
    ]

    for user_id, name, specialization, phone, address, schedule in sample_doctors:
        cursor.execute('''
        INSERT INTO doctors (user_id, name, specialization, phone, address, schedule)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, name, specialization, phone, address, schedule))

    # Create patients table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        phone TEXT,
        address TEXT,
        medical_history TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Add sample patients
    sample_patients = [
        (4, 'James Wilson', 35, 'Male', '+1234567892', '789 Patient St', 'No major issues'),
        (5, 'Emma Davis', 28, 'Female', '+1234567893', '321 Health Ave', 'Allergic to penicillin')
    ]

    for user_id, name, age, gender, phone, address, history in sample_patients:
        cursor.execute('''
        INSERT INTO patients (user_id, name, age, gender, phone, address, medical_history)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, age, gender, phone, address, history))

    # Create appointments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        appointment_date DATETIME,
        status TEXT,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients (id),
        FOREIGN KEY (doctor_id) REFERENCES doctors (id)
    )
    ''')

    # Create prescriptions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER,
        medication TEXT NOT NULL,
        dosage TEXT NOT NULL,
        instructions TEXT,
        prescribed_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (appointment_id) REFERENCES appointments (id)
    )
    ''')

    # Add sample appointments
    sample_appointments = [
        (1, 1, '2024-03-20 10:00:00', 'Scheduled', 'Regular checkup'),
        (2, 2, '2024-03-21 14:30:00', 'Scheduled', 'Follow-up appointment'),
        (1, 3, '2024-03-22 11:00:00', 'Scheduled', 'Initial consultation'),
        (2, 4, '2024-03-23 15:00:00', 'Scheduled', 'Routine checkup')
    ]

    for patient_id, doctor_id, date, status, description in sample_appointments:
        cursor.execute('''
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, description)
        VALUES (?, ?, ?, ?, ?)
        ''', (patient_id, doctor_id, date, status, description))

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
  