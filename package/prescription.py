from flask_restful import Resource, reqparse
from flask import jsonify
import sqlite3
from datetime import datetime

class Prescription(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('appointment_id', type=int)
        self.parser.add_argument('medication', type=str)
        self.parser.add_argument('dosage', type=str)
        self.parser.add_argument('instructions', type=str)

    def get(self, id):
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, a.patient_id, a.doctor_id 
            FROM prescriptions p
            JOIN appointments a ON p.appointment_id = a.id
            WHERE p.id = ?
        ''', (id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'appointment_id': row[1],
                'medication': row[2],
                'dosage': row[3],
                'instructions': row[4],
                'prescribed_date': row[5],
                'patient_id': row[6],
                'doctor_id': row[7]
            }
        return {'message': 'Prescription not found'}, 404

class Prescriptions(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('appointment_id', type=int, required=True)
        self.parser.add_argument('medication', type=str, required=True)
        self.parser.add_argument('dosage', type=str, required=True)
        self.parser.add_argument('instructions', type=str)

    def post(self):
        args = self.parser.parse_args()
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO prescriptions (
                    appointment_id, medication, dosage, instructions
                ) VALUES (?, ?, ?, ?)
            ''', (
                args['appointment_id'],
                args['medication'],
                args['dosage'],
                args['instructions']
            ))
            
            prescription_id = cursor.lastrowid
            conn.commit()

            return {
                'id': prescription_id,
                'message': 'Prescription created successfully'
            }, 201

        except sqlite3.Error as e:
            conn.rollback()
            return {'message': f'Database error: {str(e)}'}, 500
        finally:
            conn.close()

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('appointment_id', type=int, location='args')
        parser.add_argument('patient_id', type=int, location='args')
        args = parser.parse_args()

        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()

        query = '''
            SELECT p.*, a.patient_id, a.doctor_id 
            FROM prescriptions p
            JOIN appointments a ON p.appointment_id = a.id
        '''
        params = []

        if args['appointment_id']:
            query += ' WHERE p.appointment_id = ?'
            params.append(args['appointment_id'])
        elif args['patient_id']:
            query += ' WHERE a.patient_id = ?'
            params.append(args['patient_id'])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [{
            'id': row[0],
            'appointment_id': row[1],
            'medication': row[2],
            'dosage': row[3],
            'instructions': row[4],
            'prescribed_date': row[5],
            'patient_id': row[6],
            'doctor_id': row[7]
        } for row in rows] 