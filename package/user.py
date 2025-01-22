from flask_restful import Resource, reqparse
from flask import jsonify, session
import hashlib
import os
import sqlite3

class User:
    def __init__(self, username, password, role):
        self.username = username
        salt = os.urandom(32)
        self.password = self._hash_password(password, salt)
        self.role = role

    @staticmethod
    def _hash_password(password, salt=None):
        if salt is None:
            salt = os.urandom(32)
        hash_obj = hashlib.sha256(salt + password.encode('utf-8'))
        return salt.hex() + hash_obj.hexdigest()

    @staticmethod
    def verify_password(stored_password, provided_password):
        try:
            salt = bytes.fromhex(stored_password[:64])
            stored_hash = stored_password[64:]
            hash_obj = hashlib.sha256(salt + provided_password.encode('utf-8'))
            return stored_hash == hash_obj.hexdigest()
        except Exception:
            return False

class Auth(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, required=True)
        self.parser.add_argument('password', type=str, required=True)

    def post(self):
        args = self.parser.parse_args()
        
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (args['username'],))
        user = cursor.fetchone()
        
        if user and User.verify_password(user[2], args['password']):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            return {'message': 'Login successful', 'role': user[3]}, 200
        
        return {'message': 'Invalid credentials'}, 401

class Users(Resource):
    def get(self):
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.username, u.role,
                   d.name as doctor_name,
                   p.name as patient_name
            FROM users u
            LEFT JOIN doctors d ON u.id = d.user_id
            LEFT JOIN patients p ON u.id = p.user_id
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'username': row[1],
            'role': row[2],
            'name': row[3] if row[2] == 'doctor' else row[4] if row[2] == 'patient' else None
        } for row in rows]

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('user_type', type=str, required=True)
        args = parser.parse_args()
        
        role = args['user_type']
        
        try:
            user = User(args['username'], args['password'], role)
            
            conn = sqlite3.connect('hospital.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM users WHERE username = ?', (args['username'],))
            if cursor.fetchone():
                return {'message': 'Username already exists'}, 400
            
            cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', (user.username, user.password, user.role))
            
            user_id = cursor.lastrowid
            
            if role == 'patient':
                cursor.execute('''
                    INSERT INTO patients (user_id, name)
                    VALUES (?, ?)
                ''', (user_id, args['username']))
            elif role == 'doctor':
                cursor.execute('''
                    INSERT INTO doctors (user_id, name)
                    VALUES (?, ?)
                ''', (user_id, args['username']))
            
            conn.commit()
            return {'id': user_id, 'message': 'User created successfully'}, 201
            
        except sqlite3.IntegrityError as e:
            print(f"Database integrity error: {str(e)}")
            return {'message': 'Username already exists'}, 400
        except Exception as e:
            print(f"Unexpected error during user creation: {str(e)}")
            return {'message': f'An error occurred while creating user: {str(e)}'}, 500
        finally:
            conn.close()

class UserResource(Resource):
    def delete(self, id):
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        
        try:
            # Check if user exists and is not an admin
            cursor.execute('SELECT role FROM users WHERE id = ?', (id,))
            user = cursor.fetchone()
            
            if not user:
                return {'message': 'User not found'}, 404
            
            if user[0] == 'admin':
                return {'message': 'Cannot delete admin user'}, 403
            
            # Delete associated records first
            if user[0] == 'doctor':
                cursor.execute('DELETE FROM doctors WHERE user_id = ?', (id,))
            elif user[0] == 'patient':
                cursor.execute('DELETE FROM patients WHERE user_id = ?', (id,))
            
            # Delete the user
            cursor.execute('DELETE FROM users WHERE id = ?', (id,))
            conn.commit()
            
            return {'message': 'User deleted successfully'}
            
        except sqlite3.Error as e:
            return {'message': f'Database error: {str(e)}'}, 500
        finally:
            conn.close()