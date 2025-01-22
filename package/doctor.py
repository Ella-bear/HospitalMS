from flask_restful import Resource, reqparse
from flask import jsonify
import sqlite3

class Doctor(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str)
        self.parser.add_argument('specialization', type=str)
        self.parser.add_argument('phone', type=str)
        self.parser.add_argument('address', type=str)
        self.parser.add_argument('schedule', type=str)

    def get(self, id):
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM doctors WHERE id = ?', (id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'name': row[2],
                'specialization': row[3],
                'phone': row[4],
                'address': row[5],
                'schedule': row[6]
            }
        return {'message': 'Doctor not found'}, 404

    def put(self, id):
        args = self.parser.parse_args()
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE doctors 
            SET name=?, specialization=?, phone=?, address=?, schedule=?
            WHERE id=?
        ''', (
            args['name'],
            args['specialization'],
            args['phone'],
            args['address'],
            args['schedule'],
            id
        ))
        
        conn.commit()
        conn.close()
        return {'message': 'Doctor updated'}

class Doctors(Resource):
    def get(self):
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM doctors')
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'user_id': row[1],
            'name': row[2],
            'specialization': row[3],
            'phone': row[4],
            'address': row[5],
            'schedule': row[6]
        } for row in rows]

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('specialization', type=str, required=True)
        parser.add_argument('phone', type=str)
        parser.add_argument('address', type=str)
        parser.add_argument('schedule', type=str)
        
        args = parser.parse_args()
        
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO doctors (user_id, name, specialization, phone, address, schedule)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            args['user_id'],
            args['name'],
            args['specialization'],
            args['phone'],
            args['address'],
            args['schedule']
        ))
        
        doctor_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {'id': doctor_id, 'message': 'Doctor created'}, 201