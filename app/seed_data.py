from datetime import datetime, timedelta
from faker import Faker
import random
from typing import List, Dict, Any
from .models import Lead, Task, Note, Appointment, Vehicle
from .db import db

# Initialize Faker
fake = Faker()

# Constants
LEAD_STATUSES = ["NEW", "CONTACTED", "QUALIFIED", "UNQUALIFIED", "CUSTOMER"]
LEAD_SOURCES = ["Website", "Referral", "Walk-in", "Phone Inquiry", "Email", "Social Media"]
TASK_STATUSES = ["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED"]
TASK_PRIORITIES = ["LOW", "MEDIUM", "HIGH", "URGENT"]
APPOINTMENT_STATUSES = ["SCHEDULED", "CONFIRMED", "COMPLETED", "CANCELLED", "NO_SHOW"]
VEHICLE_MAKES = ["Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "Hyundai", "Kia", "Subaru", "Jeep", "BMW"]
VEHICLE_MODELS = {
    "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Tacoma", "4Runner", "Sienna", "Tundra", "Prius", "Avalon"],
    "Honda": ["Civic", "Accord", "CR-V", "Pilot", "HR-V", "Odyssey", "Ridgeline", "Passport", "Insight", "Fit"],
    "Ford": ["F-150", "Escape", "Explorer", "Mustang", "Edge", "Expedition", "Ranger", "Bronco", "Maverick", "Transit"],
    "Chevrolet": ["Silverado", "Equinox", "Tahoe", "Traverse", "Malibu", "Trailblazer", "Blazer", "Suburban", "Camaro", "Colorado"],
    "Nissan": ["Rogue", "Altima", "Sentra", "Rogue Sport", "Murano", "Pathfinder", "Frontier", "Titan", "Versa", "Kicks"],
    "Hyundai": ["Tucson", "Santa Fe", "Elantra", "Sonata", "Kona", "Palisade", "Venue", "Ioniq", "Nexo", "Veloster"],
    "Kia": ["Telluride", "Sorento", "Sportage", "Seltos", "Soul", "Forte", "K5", "Carnival", "Stinger", "Niro"],
    "Subaru": ["Outback", "Forester", "Crosstrek", "Ascent", "Legacy", "Impreza", "WRX", "BRZ", "Baja", "Tribeca"],
    "Jeep": ["Grand Cherokee", "Wrangler", "Cherokee", "Compass", "Renegade", "Gladiator", "Wagoneer", "Liberty", "Commander", "Patriot"],
    "BMW": ["3 Series", "5 Series", "X3", "X5", "X7", "4 Series", "7 Series", "X1", "X6", "2 Series"]
}
VEHICLE_CONDITIONS = ["NEW", "USED", "CERTIFIED_PREOWNED"]
VEHICLE_COLORS = ["Black", "White", "Silver", "Gray", "Red", "Blue", "Green", "Yellow", "Orange", "Purple"]

def seed_database():
    """Seed the in-memory database with sample data"""
    # Clear existing data
    db.clear()
    
    # Create sample leads
    leads = []
    for _ in range(100):
        lead = db.create(Lead, 
                         name=fake.name(),
                         email=fake.email(),
                         phone=fake.phone_number(),
                         lead_status=random.choice(LEAD_STATUSES),
                         lead_source=random.choice(LEAD_SOURCES),
                         lead_owner=fake.name())
        leads.append(lead)
    
    # Create sample tasks
    tasks = []
    for lead in leads:
        task = db.create(Task,
                         title=fake.bs(),
                         description=fake.paragraph(),
                         due_date=(datetime.utcnow() + timedelta(days=random.randint(1, 30))).isoformat(),
                         status=random.choice(TASK_STATUSES),
                         priority=random.choice(TASK_PRIORITIES),
                         assignee=fake.name(),
                         lead_id=lead.id)
        tasks.append(task)
    
    # Create sample notes
    notes = []
    for lead in leads:
        note = db.create(Note,
                         title=fake.bs(),
                         content=fake.paragraph(),
                         author=fake.name(),
                         lead_id=lead.id)
        notes.append(note)
    
    for task in tasks:
        note = db.create(Note,
                         title=fake.bs(),
                         content=fake.paragraph(),
                         author=fake.name(),
                         task_id=task.id)
        notes.append(note)
    
    # Create sample appointments
    appointments = []
    for lead in leads:
        appointment = db.create(Appointment,
                                title=fake.bs(),
                                description=fake.paragraph(),
                                location=fake.address(),
                                start_time=(datetime.utcnow() + timedelta(days=random.randint(1, 30), hours=random.randint(8, 17))).isoformat(),
                                end_time=(datetime.utcnow() + timedelta(days=random.randint(1, 30), hours=random.randint(9, 18))).isoformat(),
                                status=random.choice(APPOINTMENT_STATUSES),
                                lead_id=lead.id)
        appointments.append(appointment)
    
    # Create sample vehicles
    vehicles = []
    for lead in leads:
        make = random.choice(VEHICLE_MAKES)
        model = random.choice(VEHICLE_MODELS[make])  # Select a model based on the make
        
        vehicle = db.create(Vehicle,
                         make=make,
                         model=model,
                         year=str(random.randint(2010, 2023)),
                         color=random.choice(VEHICLE_COLORS),
                         vin=fake.vin(),
                         mileage=random.randint(1000, 150000),
                         condition=random.choice(VEHICLE_CONDITIONS),
                         notes=fake.sentence(),
                         lead_id=lead.id)
        vehicles.append(vehicle)
    
    # Set up relationships
    for lead in leads:
        db.add_relationship(Lead, lead.id, 'tasks', Task, random.choice(tasks).id)
        db.add_relationship(Lead, lead.id, 'notes', Note, random.choice(notes).id)
        db.add_relationship(Lead, lead.id, 'appointments', Appointment, random.choice(appointments).id)
        db.add_relationship(Lead, lead.id, 'vehicles', Vehicle, random.choice(vehicles).id)
    
    return {
        'leads': leads,
        'tasks': tasks,
        'notes': notes,
        'appointments': appointments,
        'vehicles': vehicles
    }