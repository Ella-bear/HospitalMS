#Tushar Borole
#Python 2.7

from flask_restful import Resource, reqparse
from flask import jsonify
import sqlite3
from datetime import datetime



class Appointment(Resource):
    """This contain all api doing activity with single appointment"""

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('patient_id', type=int)
        self.parser.add_argument('doctor_id', type=int)
        self.parser.add_argument('appointment_date', type=str)
        self.parser.add_argument('status', type=str)
        self.parser.add_argument('description', type=str)

    def get(self, id):
        """retrive a singe appointment details by its id"""

        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, p.name as patient_name, d.name as doctor_name 
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            WHERE a.id = ?
        ''', (id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'patient_id': row[1],
                'doctor_id': row[2],
                'appointment_date': row[3],
                'status': row[4],
                'description': row[5],
                'created_at': row[6],
                'patient_name': row[7],
                'doctor_name': row[8]
            }
        return {'message': 'Appointment not found'}, 404

    def put(self, id):
        """Update the appointment details by the appointment id"""

        args = self.parser.parse_args()
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE appointments 
            SET patient_id=?, doctor_id=?, appointment_date=?, status=?, description=?
            WHERE id=?
        ''', (
            args['patient_id'], 
            args['doctor_id'],
            args['appointment_date'],
            args['status'],
            args['description'],
            id
        ))
        
        conn.commit()
        conn.close()
        return {'message': 'Appointment updated'}

    def delete(self, id):
        """Delete teh appointment by its id"""

        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM appointments WHERE id=?', (id,))
        conn.commit()
        conn.close()
        return {'message': 'Appointment deleted'}



class Appointments(Resource):
    """This contain apis to carry out activity with all appiontments"""

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('patient_id', type=int, required=True, help='Patient ID is required')
        self.parser.add_argument('doctor_id', type=int, required=True, help='Doctor ID is required')
        self.parser.add_argument('appointment_date', type=str, required=True, help='Appointment date is required')
        self.parser.add_argument('status', type=str)
        self.parser.add_argument('description', type=str, required=True, help='Description is required')

    def get(self):
        """Retrive all the appointment and return in form of json"""

        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        
        # Get query parameters for filtering
        parser = reqparse.RequestParser()
        parser.add_argument('doctor_id', type=int, location='args')
        parser.add_argument('patient_id', type=int, location='args')
        args = parser.parse_args()

        query = '''
            SELECT a.*, p.name as patient_name, d.name as doctor_name 
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
        '''
        params = []

        if args['doctor_id']:
            query += ' WHERE a.doctor_id = ?'
            params.append(args['doctor_id'])
        elif args['patient_id']:
            query += ' WHERE a.patient_id = ?'
            params.append(args['patient_id'])

        query += ' ORDER BY a.appointment_date DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [{
            'id': row[0],
            'patient_id': row[1],
            'doctor_id': row[2],
            'appointment_date': row[3],
            'status': row[4],
            'description': row[5],
            'created_at': row[6],
            'patient_name': row[7],
            'doctor_name': row[8]
        } for row in rows]

    def post(self):
        """Create the appoitment by assiciating patient and docter with appointment date"""

        args = self.parser.parse_args()
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()

        try:
            # Validate that the doctor exists
            cursor.execute('SELECT id FROM doctors WHERE id = ?', (args['doctor_id'],))
            if not cursor.fetchone():
                return {'message': 'Doctor not found'}, 404

            # Validate that the patient exists
            cursor.execute('SELECT id FROM patients WHERE id = ?', (args['patient_id'],))
            if not cursor.fetchone():
                return {'message': 'Patient not found'}, 404

            # Insert the appointment
            cursor.execute('''
                INSERT INTO appointments (
                    patient_id, 
                    doctor_id, 
                    appointment_date, 
                    status, 
                    description
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                args['patient_id'],
                args['doctor_id'],
                args['appointment_date'],
                args.get('status', 'Scheduled'),
                args['description']
            ))
            
            appointment_id = cursor.lastrowid
            conn.commit()

            # Fetch the created appointment with doctor and patient names
            cursor.execute('''
                SELECT a.*, p.name as patient_name, d.name as doctor_name 
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                JOIN doctors d ON a.doctor_id = d.id
                WHERE a.id = ?
            ''', (appointment_id,))
            
            row = cursor.fetchone()
            
            return {
                'message': 'Appointment created successfully',
                'appointment': {
                    'id': row[0],
                    'patient_id': row[1],
                    'doctor_id': row[2],
                    'appointment_date': row[3],
                    'status': row[4],
                    'description': row[5],
                    'created_at': row[6],
                    'patient_name': row[7],
                    'doctor_name': row[8]
                }
            }, 201

        except sqlite3.Error as e:
            conn.rollback()
            return {'message': f'Database error: {str(e)}'}, 500
        finally:
            conn.close()



def create_sample_appointments():
    """Create sample appointments if none exist"""
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    # Check if there are any appointments
    cursor.execute('SELECT COUNT(*) FROM appointments')
    count = cursor.fetchone()[0]

    if count == 0:
        # Get existing patient and doctor IDs
        cursor.execute('SELECT id FROM patients LIMIT 2')
        patient_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute('SELECT id FROM doctors LIMIT 2')
        doctor_ids = [row[0] for row in cursor.fetchall()]

        if patient_ids and doctor_ids:
            # Sample appointments data
            sample_appointments = [
                (patient_ids[0], doctor_ids[0], '2024-03-20 10:00:00', 'Scheduled', 'Regular checkup'),
                (patient_ids[0], doctor_ids[1], '2024-03-21 14:30:00', 'Scheduled', 'Follow-up appointment'),
                (patient_ids[1], doctor_ids[0], '2024-03-22 11:00:00', 'Scheduled', 'Initial consultation'),
                (patient_ids[1], doctor_ids[1], '2024-03-23 15:00:00', 'Scheduled', 'Routine checkup')
            ]

            cursor.executemany('''
                INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, description)
                VALUES (?, ?, ?, ?, ?)
            ''', sample_appointments)

            conn.commit()
            print("Sample appointments created successfully!")

    conn.close()