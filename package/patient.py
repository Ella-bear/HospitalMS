#Tushar Borole
#Python 2.7

from flask_restful import Resource, reqparse
from flask import jsonify
import sqlite3

class Patient(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str)
        self.parser.add_argument('age', type=int)
        self.parser.add_argument('gender', type=str)
        self.parser.add_argument('phone', type=str)
        self.parser.add_argument('address', type=str)
        self.parser.add_argument('medical_history', type=str)

    def get(self, id):
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        
        # First try to find patient by ID
        cursor.execute('SELECT * FROM patients WHERE id = ?', (id,))
        row = cursor.fetchone()
        
        # If not found, try to find by user_id
        if not row:
            cursor.execute('SELECT * FROM patients WHERE user_id = ?', (id,))
            row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'name': row[2],
                'age': row[3],
                'gender': row[4],
                'phone': row[5],
                'address': row[6],
                'medical_history': row[7]
            }
        return {'message': 'Patient not found'}, 404

class Patients(Resource):
    def get(self):
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients')
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'user_id': row[1],
            'name': row[2],
            'age': row[3],
            'gender': row[4],
            'phone': row[5],
            'address': row[6],
            'medical_history': row[7]
        } for row in rows]