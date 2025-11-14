"""
Automatic Hostel Room Allotment System - Flask Web Application
Author: Sai Viresh Salpure
"""

from flask import Flask, render_template_string, request, jsonify
from dataclasses import dataclass, field
import json
import os

app = Flask(__name__)
DATA_FILE = "hostel_data.json"

# -------------------- Models --------------------
@dataclass
class Room:
    number: str
    capacity: int
    floor: int
    type: str = "Standard"
    occupied: int = 0
    students: list = field(default_factory=list)

    def is_available(self): 
        return self.occupied < self.capacity
    
    def add_student(self, sid):
        if self.is_available():
            self.students.append(sid)
            self.occupied += 1
            return True
        return False
    
    def to_dict(self):
        return {
            'number': self.number,
            'capacity': self.capacity,
            'floor': self.floor,
            'type': self.type,
            'occupied': self.occupied,
            'students': self.students
        }
    
    @staticmethod
    def from_dict(data):
        return Room(
            number=data['number'],
            capacity=data['capacity'],
            floor=data['floor'],
            type=data.get('type', 'Standard'),
            occupied=data.get('occupied', 0),
            students=data.get('students', [])
        )


@dataclass
class Student:
    sid: str
    name: str
    gender: str
    year: int
    room: str = None
    
    def to_dict(self):
        return {
            'sid': self.sid,
            'name': self.name,
            'gender': self.gender,
            'year': self.year,
            'room': self.room
        }
    
    @staticmethod
    def from_dict(data):
        return Student(
            sid=data['sid'],
            name=data['name'],
            gender=data['gender'],
            year=data['year'],
            room=data.get('room')
        )


# -------------------- System --------------------
class HostelSystem:
    def __init__(self):
        self.rooms = []
        self.students = []
        self.load_data()

    def save_data(self):
        data = {
            'rooms': [r.to_dict() for r in self.rooms],
            'students': [s.to_dict() for s in self.students]
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE) as f:
                    data = json.load(f)
                    self.rooms = [Room.from_dict(r) for r in data.get('rooms', [])]
                    self.students = [Student.from_dict(s) for s in data.get('students', [])]
            except Exception as e:
                print(f"Error loading data: {e}")
                self.rooms, self.students = [], []

    def add_room(self, number, capacity, floor, rtype):
        self.rooms.append(Room(number, int(capacity), int(floor), rtype))
        self.save_data()
        return True

    def add_student(self, sid, name, gender, year):
        self.students.append(Student(sid, name, gender, int(year)))
        self.save_data()
        return True

    def get_student_by_id(self, sid):
        return next((s for s in self.students if s.sid == sid), None)

    def allocate_rooms(self):
        if not self.rooms: 
            return {"success": False, "message": "No rooms available!"}
        if not self.students: 
            return {"success": False, "message": "No students available!"}
        
        log = []
        sorted_students = sorted(self.students, key=lambda s: s.year, reverse=True)
        
        for gender_group in ["male", "female"]:
            for s in [st for st in sorted_students if st.gender.lower() == gender_group]:
                allocated = False
                for r in self.rooms:
                    if r.is_available() and r.add_student(s.sid):
                        s.room = r.number
                        log.append({"student": s.name, "room": r.number, "status": "success"})
                        allocated = True
                        break
                if not allocated:
                    log.append({"student": s.name, "room": None, "status": "failed"})
        
        self.save_data()
        return {"success": True, "log": log}

    def get_stats(self):
        total_rooms = len(self.rooms)
        total_capacity = sum(r.capacity for r in self.rooms)
        occupied_beds = sum(r.occupied for r in self.rooms)
        total_students = len(self.students)
        allocated_students = len([s for s in self.students if s.room])
        
        return {
            "total_rooms": total_rooms,
            "total_capacity": total_capacity,
            "occupied_beds": occupied_beds,
            "total_students": total_students,
            "allocated_students": allocated_students,
            "unallocated_students": total_students - allocated_students
        }


# Global system instance
hostel_sys = HostelSystem()

# HTML Template - Modern Professional Design
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hostel Management System</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #1a202c;
            position: relative;
            overflow-x: hidden;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: 50px 50px;
            animation: moveGrid 20s linear infinite;
            pointer-events: none;
        }
        
        @keyframes moveGrid {
            0% { transform: translate(0, 0); }
            100% { transform: translate(50px, 50px); }
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
            position: relative;
            z-index: 1;
        }
        
        .header {
            text-align: center;
            margin-bottom: 50px;
            animation: fadeInDown 0.8s ease;
        }
        
        .header h1 {
            font-size: 3.5rem;
            font-weight: 700;
            color: white;
            margin-bottom: 10px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.2);
            letter-spacing: -1px;
        }
        
        .header p {
            font-size: 1.2rem;
            color: rgba(255,255,255,0.9);
            font-weight: 300;
        }
        
        .stats-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border: 1px solid rgba(255,255,255,0.3);
            position: relative;
            overflow: hidden;
            animation: fadeInUp 0.6s ease backwards;
        }
        
        .stat-card:nth-child(1) { animation-delay: 0.1s; }
        .stat-card:nth-child(2) { animation-delay: 0.2s; }
        .stat-card:nth-child(3) { animation-delay: 0.3s; }
        .stat-card:nth-child(4) { animation-delay: 0.4s; }
        .stat-card:nth-child(5) { animation-delay: 0.5s; }
        .stat-card:nth-child(6) { animation-delay: 0.6s; }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 30px 80px rgba(0,0,0,0.25);
        }
        
        .stat-card:hover::before {
            opacity: 1;
        }
        
        .stat-icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
            display: inline-block;
            animation: bounce 2s infinite;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 10px 0;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }
        
        .main-card {
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(20px);
            border-radius: 30px;
            overflow: hidden;
            box-shadow: 0 30px 90px rgba(0,0,0,0.2);
            animation: fadeInUp 0.8s ease 0.3s backwards;
        }
        
        .tabs {
            display: flex;
            background: linear-gradient(to right, #f7fafc, #edf2f7);
            padding: 10px;
            gap: 10px;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .tab-btn {
            flex: 1;
            padding: 18px 25px;
            border: none;
            background: transparent;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            color: #718096;
            border-radius: 15px;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
        }
        
        .tab-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea, #764ba2);
            transition: left 0.3s;
            z-index: -1;
        }
        
        .tab-btn:hover {
            color: #4a5568;
            transform: translateY(-2px);
        }
        
        .tab-btn.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .tab-btn.active::before {
            left: 0;
        }
        
        .tab-content {
            display: none;
            padding: 40px;
            animation: fadeIn 0.5s ease;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .section-title {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 30px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .form-container {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 40px;
            border: 2px solid rgba(102, 126, 234, 0.1);
            transition: all 0.3s;
        }
        
        .form-container:hover {
            border-color: rgba(102, 126, 234, 0.3);
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.1);
        }
        
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        
        .form-group {
            position: relative;
        }
        
        .form-group label {
            display: block;
            font-size: 0.85rem;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .form-group input,
        .form-group select {
            width: 100%;
            padding: 14px 18px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 1rem;
            font-family: 'Inter', sans-serif;
            background: white;
            transition: all 0.3s;
            color: #2d3748;
        }
        
        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
            transform: translateY(-2px);
        }
        
        .btn {
            padding: 15px 35px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255,255,255,0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        
        .btn:hover::before {
            width: 300px;
            height: 300px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            box-shadow: 0 10px 30px rgba(72, 187, 120, 0.3);
        }
        
        .btn-success:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(72, 187, 120, 0.4);
        }
        
        .table-container {
            overflow-x: auto;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }
        
        .data-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            background: white;
        }
        
        .data-table thead tr {
            background: linear-gradient(135deg, #667eea, #764ba2);
        }
        
        .data-table th {
            padding: 18px;
            text-align: left;
            font-weight: 600;
            color: white;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .data-table th:first-child {
            border-top-left-radius: 15px;
        }
        
        .data-table th:last-child {
            border-top-right-radius: 15px;
        }
        
        .data-table td {
            padding: 18px;
            border-bottom: 1px solid #f0f0f0;
            color: #2d3748;
            transition: background 0.3s;
        }
        
        .data-table tbody tr {
            transition: all 0.3s;
        }
        
        .data-table tbody tr:hover {
            background: linear-gradient(to right, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
            transform: scale(1.01);
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        
        .badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .badge-success {
            background: linear-gradient(135deg, #48bb78, #38a169);
            color: white;
            box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
        }
        
        .badge-warning {
            background: linear-gradient(135deg, #ed8936, #dd6b20);
            color: white;
            box-shadow: 0 4px 15px rgba(237, 137, 54, 0.3);
        }
        
        .badge-danger {
            background: linear-gradient(135deg, #f56565, #e53e3e);
            color: white;
            box-shadow: 0 4px 15px rgba(245, 101, 101, 0.3);
        }
        
        .badge-info {
            background: linear-gradient(135deg, #4299e1, #3182ce);
            color: white;
            box-shadow: 0 4px 15px rgba(66, 153, 225, 0.3);
        }
        
        .alert {
            padding: 20px 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 15px;
            animation: slideInLeft 0.5s ease;
        }
        
        .alert-info {
            background: linear-gradient(135deg, rgba(66, 153, 225, 0.1), rgba(49, 130, 206, 0.1));
            border-left: 4px solid #4299e1;
            color: #2c5282;
        }
        
        .allocation-log {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-top: 30px;
            max-height: 500px;
            overflow-y: auto;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        
        .allocation-log::-webkit-scrollbar {
            width: 8px;
        }
        
        .allocation-log::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        .allocation-log::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 10px;
        }
        
        .log-item {
            padding: 15px 20px;
            margin-bottom: 12px;
            border-radius: 12px;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 12px;
            animation: slideInRight 0.3s ease;
            transition: all 0.3s;
        }
        
        .log-item:hover {
            transform: translateX(5px);
        }
        
        .log-item.success {
            background: linear-gradient(135deg, rgba(72, 187, 120, 0.1), rgba(56, 161, 105, 0.1));
            border-left: 4px solid #48bb78;
            color: #22543d;
        }
        
        .log-item.failed {
            background: linear-gradient(135deg, rgba(245, 101, 101, 0.1), rgba(229, 62, 62, 0.1));
            border-left: 4px solid #f56565;
            color: #742a2a;
        }
        
        .room-card {
            background: white;
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            transition: all 0.3s;
            border: 2px solid transparent;
            animation: fadeInUp 0.5s ease;
        }
        
        .room-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 50px rgba(0,0,0,0.15);
            border-color: rgba(102, 126, 234, 0.3);
        }
        
        .room-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .room-title {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .room-info {
            color: #718096;
            margin-bottom: 20px;
            font-size: 0.95rem;
        }
        
        .student-list {
            list-style: none;
        }
        
        .student-list li {
            padding: 15px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
            margin-bottom: 10px;
            border-radius: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
            border-left: 3px solid #667eea;
        }
        
        .student-list li:hover {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
            transform: translateX(5px);
        }
        
        .toast {
            position: fixed;
            top: 30px;
            right: 30px;
            background: white;
            padding: 20px 30px;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            z-index: 1000;
            display: none;
            border-left: 5px solid #48bb78;
            animation: slideInRight 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .toast.show {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .toast::before {
            content: '✓';
            display: flex;
            align-items: center;
            justify-content: center;
            width: 30px;
            height: 30px;
            background: linear-gradient(135deg, #48bb78, #38a169);
            color: white;
            border-radius: 50%;
            font-weight: bold;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(40px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-40px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(100px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-100px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2.5rem;
            }
            .stats-container {
                grid-template-columns: repeat(2, 1fr);
            }
            .form-grid {
                grid-template-columns: 1fr;
            }
            .tabs {
                flex-wrap: wrap;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 Hostel Management System</h1>
            <p>Intelligent Room Allocation Platform</p>
        </div>

        <div class="stats-container" id="statsContainer"></div>

        <div class="main-card">
            <div class="tabs">
                <button class="tab-btn active" onclick="switchTab('rooms')">🏢 Rooms</button>
                <button class="tab-btn" onclick="switchTab('students')">👥 Students</button>
                <button class="tab-btn" onclick="switchTab('allocate')">🎯 Allocate</button>
                <button class="tab-btn" onclick="switchTab('report')">📊 Reports</button>
            </div>

            <div class="tab-content active" id="rooms-tab">
                <h2 class="section-title">Room Management</h2>
                <div class="form-container">
                    <form id="roomForm" onsubmit="addRoom(event)">
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Room Number</label>
                                <input type="text" name="number" required placeholder="e.g., 101">
                            </div>
                            <div class="form-group">
                                <label>Capacity</label>
                                <input type="number" name="capacity" min="1" required placeholder="e.g., 2">
                            </div>
                            <div class="form-group">
                                <label>Floor</label>
                                <input type="number" name="floor" min="0" required placeholder="e.g., 1">
                            </div>
                            <div class="form-group">
                                <label>Room Type</label>
                                <select name="type">
                                    <option>Standard</option>
                                    <option>Deluxe</option>
                                    <option>AC</option>
                                </select>
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary">Add Room</button>
                    </form>
                </div>

                <div class="table-container">
                    <table class="data-table" id="roomsTable">
                        <thead>
                            <tr>
                                <th>Room No.</th>
                                <th>Floor</th>
                                <th>Type</th>
                                <th>Capacity</th>
                                <th>Occupied</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>

            <div class="tab-content" id="students-tab">
                <h2 class="section-title">Student Management</h2>
                <div class="form-container">
                    <form id="studentForm" onsubmit="addStudent(event)">
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Student ID</label>
                                <input type="text" name="sid" required placeholder="e.g., S001">
                            </div>
                            <div class="form-group">
                                <label>Full Name</label>
                                <input type="text" name="name" required placeholder="e.g., John Doe">
                            </div>
                            <div class="form-group">
                                <label>Gender</label>
                                <select name="gender">
                                    <option>Male</option>
                                    <option>Female</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Year</label>
                                <input type="number" name="year" min="1" max="4" required placeholder="1-4">
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary">Add Student</button>
                    </form>
                </div>

                <div class="table-container">
                    <table class="data-table" id="studentsTable">
                        <thead>
                            <tr>
                                <th>Student ID</th>
                                <th>Name</th>
                                <th>Gender</th>
                                <th>Year</th>
                                <th>Room Assigned</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>

            <div class="tab-content" id="allocate-tab">
                <h2 class="section-title">Automatic Room Allocation</h2>
                <div class="alert alert-info">
                    <span style="font-size: 1.5rem;">ℹ️</span>
                    <span>This will automatically allocate rooms to students based on year priority (senior students first) and room availability.</span>
                </div>
                <button class="btn btn-success" onclick="allocateRooms()">🚀 Start Allocation</button>
                <div class="allocation-log" id="allocationLog" style="display: none;"></div>
            </div>

            <div class="tab-content" id="report-tab">
                <h2 class="section-title">Allocation Report</h2>
                <button class="btn btn-primary" onclick="loadReport()">🔄 Generate Report</button>
                <div id="reportContainer" style="margin-top: 30px;"></div>
            </div>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        function switchTab(tabName) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tabName + '-tab').classList.add('active');
            if (tabName === 'rooms') loadRooms();
            if (tabName === 'students') loadStudents();
            if (tabName === 'report') loadReport();
        }

        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.innerHTML = '<span>' + message + '</span>';
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
        }

        async function loadStats() {
            const res = await fetch('/api/stats');
            const stats = await res.json();
            document.getElementById('statsContainer').innerHTML = `
                <div class="stat-card">
                    <div class="stat-icon">🏢</div>
                    <div class="stat-value">${stats.total_rooms}</div>
                    <div class="stat-label">Total Rooms</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📦</div>
                    <div class="stat-value">${stats.total_capacity}</div>
                    <div class="stat-label">Total Capacity</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🛏️</div>
                    <div class="stat-value">${stats.occupied_beds}</div>
                    <div class="stat-label">Occupied Beds</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">👥</div>
                    <div class="stat-value">${stats.total_students}</div>
                    <div class="stat-label">Total Students</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">✅</div>
                    <div class="stat-value">${stats.allocated_students}</div>
                    <div class="stat-label">Allocated</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">⏳</div>
                    <div class="stat-value">${stats.unallocated_students}</div>
                    <div class="stat-label">Pending</div>
                </div>
            `;
        }

        async function addRoom(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            const res = await fetch('/api/rooms', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const result = await res.json();
            if (result.success) {
                showToast('Room added successfully! 🎉');
                e.target.reset();
                loadRooms();
                loadStats();
            }
        }

        async function loadRooms() {
            const res = await fetch('/api/rooms');
            const rooms = await res.json();
            const tbody = document.querySelector('#roomsTable tbody');
            tbody.innerHTML = rooms.map(r => `
                <tr>
                    <td><strong>${r.number}</strong></td>
                    <td>Floor ${r.floor}</td>
                    <td>${r.type}</td>
                    <td>${r.capacity}</td>
                    <td>${r.occupied}</td>
                    <td>
                        ${r.available > 0 
                            ? `<span class="badge badge-success">Available (${r.available})</span>` 
                            : `<span class="badge badge-danger">Full</span>`}
                    </td>
                </tr>
            `).join('');
        }

        async function addStudent(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            const res = await fetch('/api/students', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const result = await res.json();
            if (result.success) {
                showToast('Student added successfully! 🎉');
                e.target.reset();
                loadStudents();
                loadStats();
            }
        }

        async function loadStudents() {
            const res = await fetch('/api/students');
            const students = await res.json();
            const tbody = document.querySelector('#studentsTable tbody');
            tbody.innerHTML = students.map(s => `
                <tr>
                    <td><strong>${s.sid}</strong></td>
                    <td>${s.name}</td>
                    <td>${s.gender}</td>
                    <td>Year ${s.year}</td>
                    <td>
                        ${s.room 
                            ? `<span class="badge badge-info">${s.room}</span>` 
                            : `<span class="badge badge-warning">Not Allocated</span>`}
                    </td>
                </tr>
            `).join('');
        }

        async function allocateRooms() {
            const res = await fetch('/api/allocate', {method: 'POST'});
            const result = await res.json();
            const logDiv = document.getElementById('allocationLog');
            logDiv.style.display = 'block';
            if (!result.success) {
                logDiv.innerHTML = `<div class="log-item failed">❌ ${result.message}</div>`;
                return;
            }
            logDiv.innerHTML = `
                <h3 style="margin-bottom: 20px; font-size: 1.3rem; color: #2d3748;">Allocation Results</h3>
                ${result.log.map((l, i) => `
                    <div class="log-item ${l.status}" style="animation-delay: ${i * 0.05}s">
                        <span style="font-size: 1.2rem;">${l.status === 'success' ? '✅' : '❌'}</span>
                        <strong>${l.student}</strong> 
                        <span style="margin-left: auto;">${l.room ? `→ Room ${l.room}` : '→ No room available'}</span>
                    </div>
                `).join('')}
            `;
            showToast('Allocation completed successfully! 🎉');
            loadStats();
            setTimeout(() => {
                loadStudents();
                loadRooms();
            }, 1000);
        }

        async function loadReport() {
            const res = await fetch('/api/report');
            const rooms = await res.json();
            const container = document.getElementById('reportContainer');
            if (rooms.length === 0) {
                container.innerHTML = '<div style="text-align: center; padding: 60px; color: #999;">No rooms available</div>';
                return;
            }
            container.innerHTML = rooms.map((r, i) => `
                <div class="room-card" style="animation-delay: ${i * 0.1}s">
                    <div class="room-header">
                        <div class="room-title">Room ${r.number}</div>
                        <span class="badge badge-${r.occupied === r.capacity ? 'danger' : 'success'}">
                            ${r.occupied}/${r.capacity} Occupied
                        </span>
                    </div>
                    <div class="room-info">
                        <strong>Floor:</strong> ${r.floor} | <strong>Type:</strong> ${r.type}
                    </div>
                    ${r.students.length > 0 ? `
                        <ul class="student-list">
                            ${r.students.map(s => `
                                <li>
                                    <span><strong>${s.name}</strong> (${s.sid})</span>
                                    <span class="badge badge-info">Year ${s.year}</span>
                                </li>
                            `).join('')}
                        </ul>
                    ` : '<p style="color: #999; text-align: center; padding: 20px;">No students allocated yet</p>'}
                </div>
            `).join('');
        }

        // Initialize
        loadStats();
        loadRooms();
        
        // Refresh stats every 30 seconds
        setInterval(loadStats, 30000);
    </script>
</body>
</html>"""


# -------------------- Routes --------------------
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/rooms', methods=['GET', 'POST'])
def rooms():
    if request.method == 'POST':
        data = request.json
        try:
            hostel_sys.add_room(data['number'], data['capacity'], data['floor'], data['type'])
            return jsonify({"success": True, "message": "Room added successfully"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
    return jsonify([{
        "number": r.number, "capacity": r.capacity, "floor": r.floor,
        "type": r.type, "occupied": r.occupied, "available": r.capacity - r.occupied
    } for r in hostel_sys.rooms])

@app.route('/api/students', methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        data = request.json
        try:
            hostel_sys.add_student(data['sid'], data['name'], data['gender'], data['year'])
            return jsonify({"success": True, "message": "Student added successfully"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
    return jsonify([{
        "sid": s.sid, "name": s.name, "gender": s.gender, "year": s.year, "room": s.room
    } for s in hostel_sys.students])

@app.route('/api/allocate', methods=['POST'])
def allocate():
    return jsonify(hostel_sys.allocate_rooms())

@app.route('/api/stats', methods=['GET'])
def stats():
    return jsonify(hostel_sys.get_stats())

@app.route('/api/report', methods=['GET'])
def report():
    rooms_data = []
    for r in hostel_sys.rooms:
        students_in_room = []
        for sid in r.students:
            student = hostel_sys.get_student_by_id(sid)
            if student:
                students_in_room.append({
                    "sid": student.sid,
                    "name": student.name,
                    "year": student.year
                })
        rooms_data.append({
            "number": r.number,
            "floor": r.floor,
            "type": r.type,
            "capacity": r.capacity,
            "occupied": r.occupied,
            "students": students_in_room
        })
    return jsonify(rooms_data)


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 HOSTEL MANAGEMENT SYSTEM")
    print("=" * 60)
    print("✅ Server starting...")
    print("📍 Open your browser to: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, port=5000, host='127.0.0.1')