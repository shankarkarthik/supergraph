from typing import List, Optional, Any, Dict, Union
from datetime import datetime
from ..db import db
from .types import (
    LeadType, TaskType, NoteType, AppointmentType, VehicleType,
    LeadInput, TaskInput, NoteInput, AppointmentInput, VehicleInput,
    LeadPaginationResult, TaskPaginationResult, AppointmentPaginationResult, PageInfo,
    VehicleFilterInput, AppointmentFilterInput, SortOrder, LeadFilterInput, LeadStatusCount
)
from ..models import Lead, Task, Note, Appointment, Vehicle

# Helper functions
def apply_vehicle_filters(vehicles: List[VehicleType], filters: Optional[VehicleFilterInput] = None) -> List[VehicleType]:
    if not filters:
        return vehicles

    filtered = vehicles

    if filters.make:
        if filters.make.eq:
            filtered = [v for v in filtered if v.make == filters.make.eq]
        if filters.make.contains:
            filtered = [v for v in filtered if filters.make.contains.lower() in v.make.lower()]

    if filters.model and filters.model.eq:
        filtered = [v for v in filtered if v.model == filters.model.eq]

    if filters.year and filters.year.eq:
        filtered = [v for v in filtered if v.year == filters.year.eq]

    if filters.condition and filters.condition.eq:
        filtered = [v for v in filtered if v.condition == filters.condition.eq]

    return filtered

def apply_appointment_filters(appointments: List[AppointmentType], filters: Optional[AppointmentFilterInput] = None) -> List[AppointmentType]:
    if not filters:
        return appointments

    filtered = appointments

    if filters.title:
        filtered = [a for a in filtered if filters.title.lower() in a.title.lower()]

    if filters.status:
        filtered = [a for a in filtered if a.status == filters.status]

    if filters.lead_id:
        filtered = [a for a in filtered if a.lead_id == filters.lead_id]

    if filters.start_time:
        if filters.start_time.eq:
            filtered = [a for a in filtered if a.start_time == filters.start_time.eq]
        if filters.start_time.gt:
            filtered = [a for a in filtered if a.start_time > filters.start_time.gt]
        if filters.start_time.lt:
            filtered = [a for a in filtered if a.start_time < filters.start_time.lt]
        if filters.start_time.between and len(filters.start_time.between) == 2:
            start, end = filters.start_time.between
            filtered = [a for a in filtered if start <= a.start_time <= end]

    return filtered

def paginate(items: List[Any], page: int = 0, size: int = 10) -> Dict[str, Any]:
    start = page * size
    end = start + size
    total = len(items)

    return {
        'items': items[start:end],
        'page_info': {
            'total': total,
            'page': page,
            'size': size,
            'has_next': end < total,
            'has_previous': page > 0
        }
    }

# Query Resolvers
def resolve_get_lead(id: str) -> Optional[LeadType]:
    lead = db.get(Lead, id)
    if lead:
        return LeadType(**lead.to_dict())
    return None


def resolve_get_all_leads(
        page: int = 0,
        size: int = 10,
        filter: Optional[LeadFilterInput] = None
) -> LeadPaginationResult:
    # Get all leads
    all_leads = db.get_all(Lead)

    # Get current time in ISO format for comparison
    now = datetime.utcnow().isoformat()

    # Get all appointments and group by lead_id
    all_appointments = db.get_all(Appointment)
    appointments_by_lead = {}

    for appt in all_appointments:
        if appt.lead_id not in appointments_by_lead:
            appointments_by_lead[appt.lead_id] = []
        appointments_by_lead[appt.lead_id].append(appt)

    # Process leads with filters
    filtered_leads = []

    for lead in all_leads:
        lead_dict = lead.to_dict()
        lead_appointments = appointments_by_lead.get(lead.id, [])

        # Check upcoming appointments filter if specified
        if filter and filter.has_upcoming_appointments is not None:
            has_upcoming = any(
                appt.start_time > now and appt.status in ["SCHEDULED", "CONFIRMED"]
                for appt in lead_appointments
            )
            if has_upcoming != filter.has_upcoming_appointments:
                continue

        # Apply vehicle make filter if specified
        if filter and hasattr(filter, 'vehicle_make') and filter.vehicle_make:
            lead_vehicles = [v for v in db.get_all(Vehicle) if v.lead_id == lead.id]
            has_matching_vehicle = any(
                v.make.lower() == filter.vehicle_make.lower()
                for v in lead_vehicles
            )
            if not has_matching_vehicle:
                continue

        # Apply other filters
        if filter:
            # Name filter
            if hasattr(filter, 'name') and filter.name and filter.name.eq:
                if lead_dict.get('name') != filter.name.eq:
                    continue

            # Email filter
            if hasattr(filter, 'email') and filter.email and filter.email.eq:
                if lead_dict.get('email') != filter.email.eq:
                    continue

            # Add more filters as needed...

        # If we get here, lead passes all filters
        lead_data = LeadType(**lead_dict)

        # Attach appointments to the lead
        lead_data.appointments = [
            AppointmentType(**appt.to_dict())
            for appt in lead_appointments
        ]

        filtered_leads.append(lead_data)

    # Apply pagination
    result = paginate(filtered_leads, page, size)
    return LeadPaginationResult(
        items=result['items'],
        page_info=PageInfo(**result['page_info'])
    )

def resolve_get_leads_by_status(status: str) -> LeadPaginationResult:
    leads = [
        LeadType(**lead.to_dict())
        for lead in db.get_all(Lead)
        if lead.lead_status == status
    ]
    # Using default pagination for consistency
    result = paginate(leads, 0, 10)
    return LeadPaginationResult(
        items=result['items'],
        page_info=PageInfo(**result['page_info'])
    )

def resolve_get_task(id: str) -> Optional[TaskType]:
    task = db.get(Task, id)
    if task:
        return TaskType(**task.to_dict())
    return None

def resolve_get_tasks_by_lead(lead_id: str) -> List[TaskType]:
    tasks = [
        TaskType(**task.to_dict())
        for task in db.get_all(Task)
        if task.lead_id == lead_id
    ]
    return tasks

def resolve_get_note(id: str) -> Optional[NoteType]:
    note = db.get(Note, id)
    if note:
        return NoteType(**note.to_dict())
    return None

def resolve_get_notes_by_lead(lead_id: str) -> List[NoteType]:
    notes = [
        NoteType(**note.to_dict())
        for note in db.get_all(Note)
        if note.lead_id == lead_id
    ]
    return notes

def resolve_get_notes_by_task(task_id: str) -> List[NoteType]:
    notes = [
        NoteType(**note.to_dict())
        for note in db.get_all(Note)
        if note.task_id == task_id
    ]
    return notes

def resolve_get_appointment(id: str) -> Optional[AppointmentType]:
    appointment = db.get(Appointment, id)
    if appointment:
        return AppointmentType(**appointment.to_dict())
    return None

def resolve_get_all_appointments(
    page: int = 0,
    size: int = 10,
    sort_by: str = "START_TIME",
    sort_order: str = "DESC",
    filter: Optional[AppointmentFilterInput] = None
) -> AppointmentPaginationResult:
    appointments = [AppointmentType(**a.to_dict()) for a in db.get_all(Appointment)]

    # Apply filters
    if filter:
        appointments = apply_appointment_filters(appointments, filter)

    # Apply sorting
    reverse_sort = sort_order == "DESC"

    if sort_by == "TITLE":
        appointments.sort(key=lambda x: x.title or "", reverse=reverse_sort)
    elif sort_by == "START_TIME":
        appointments.sort(key=lambda x: x.start_time, reverse=reverse_sort)
    elif sort_by == "END_TIME":
        appointments.sort(key=lambda x: x.end_time, reverse=reverse_sort)
    elif sort_by == "STATUS":
        appointments.sort(key=lambda x: x.status or "", reverse=reverse_sort)
    elif sort_by == "CREATED_AT":
        appointments.sort(key=lambda x: x.created_at, reverse=reverse_sort)

    # Apply pagination
    result = paginate(appointments, page, size)
    return AppointmentPaginationResult(
        items=result['items'],
        page_info=PageInfo(**result['page_info'])
    )

def resolve_get_vehicle(id: str) -> Optional[VehicleType]:
    vehicle = db.get(Vehicle, id)
    if vehicle:
        return VehicleType(**vehicle.to_dict())
    return None

def resolve_get_vehicles_by_lead(lead_id: str) -> List[VehicleType]:
    vehicles = [
        VehicleType(**v.to_dict())
        for v in db.get_all(Vehicle)
        if v.lead_id == lead_id
    ]
    return vehicles

def resolve_get_vehicles(
    filter: Optional[VehicleFilterInput] = None,
    sort_by: str = "CREATED_AT",
    sort_order: str = "DESC"
) -> List[VehicleType]:
    vehicles = [VehicleType(**v.to_dict()) for v in db.get_all(Vehicle)]

    # Apply filters
    if filter:
        vehicles = apply_vehicle_filters(vehicles, filter)

    # Apply sorting
    reverse_sort = sort_order == "DESC"

    if sort_by == "MAKE":
        vehicles.sort(key=lambda x: x.make or "", reverse=reverse_sort)
    elif sort_by == "MODEL":
        vehicles.sort(key=lambda x: x.model or "", reverse=reverse_sort)
    elif sort_by == "YEAR":
        vehicles.sort(key=lambda x: x.year or "", reverse=reverse_sort)
    elif sort_by == "MILEAGE":
        vehicles.sort(key=lambda x: x.mileage or 0, reverse=reverse_sort)
    elif sort_by == "CREATED_AT":
        vehicles.sort(key=lambda x: x.created_at, reverse=reverse_sort)

    return vehicles

# Field Resolvers
def resolve_lead_tasks(lead: LeadType) -> List[TaskType]:
    return [t for t in resolve_get_tasks_by_lead(lead.id)]

def resolve_lead_vehicles(lead: LeadType, filter: Optional[VehicleFilterInput] = None) -> List[VehicleType]:
    vehicles = [
        VehicleType(**v.to_dict())
        for v in db.get_all(Vehicle)
        if v.lead_id == lead.id
    ]
    if filter:
        vehicles = apply_vehicle_filters(vehicles, filter)
    return vehicles

def resolve_lead_notes(lead: LeadType) -> List[NoteType]:
    return [n for n in resolve_get_notes_by_lead(lead.id)]


def resolve_lead_appointments(lead_id: str, filter: Optional[AppointmentFilterInput] = None) -> List[AppointmentType]:
    from .types import AppointmentType
    appointments = db.get_all(Appointment)
    lead_appointments = [a for a in appointments if a.lead_id == lead_id]

    if filter and filter.status:
        if filter.status.eq:
            lead_appointments = [a for a in lead_appointments if a.status == filter.status.eq]
        if filter.status.ne:
            lead_appointments = [a for a in lead_appointments if a.status != filter.status.neq]
        if filter.status.in_list:
            lead_appointments = [a for a in lead_appointments if a.status in filter.status.in_]
        if filter.status.not_in:
            lead_appointments = [a for a in lead_appointments if a.status not in filter.status.nin]

    return [AppointmentType(**appt.to_dict()) for appt in lead_appointments]

def resolve_task_lead(task: TaskType) -> Optional[LeadType]:
    lead = db.get(Lead, task.lead_id)
    if lead:
        return LeadType(**lead.to_dict())
    return None

def resolve_task_notes(task: TaskType) -> List[NoteType]:
    return [n for n in resolve_get_notes_by_task(task.id)]

def resolve_note_lead(note: NoteType) -> Optional[LeadType]:
    if not note.lead_id:
        return None
    lead = db.get(Lead, note.lead_id)
    if lead:
        return LeadType(**lead.to_dict())
    return None

def resolve_note_task(note: NoteType) -> Optional[TaskType]:
    if not note.task_id:
        return None
    task = db.get(Task, note.task_id)
    if task:
        return TaskType(**task.to_dict())
    return None

def resolve_appointment_lead(appointment: AppointmentType) -> Optional[LeadType]:
    lead = db.get(Lead, appointment.lead_id)
    if lead:
        return LeadType(**lead.to_dict())
    return None

def resolve_appointment_notes(appointment: AppointmentType) -> List[NoteType]:
    # This is a simplified version - in a real app, you'd have a many-to-many relationship
    return [
        NoteType(**n.to_dict())
        for n in db.get_all(Note)
        if hasattr(n, 'appointment_id') and n.appointment_id == appointment.id
    ]

def resolve_vehicle_lead(vehicle: VehicleType) -> Optional[LeadType]:
    if not hasattr(vehicle, 'lead_id') or not vehicle.lead_id:
        return None

    lead = db.get(Lead, vehicle.lead_id)
    if lead:
        return LeadType(**lead.to_dict())
    return None

# Mutation Resolvers
def resolve_create_lead(input: LeadInput) -> LeadType:
    lead_data = input.__dict__.copy()
    lead = db.create(Lead, **lead_data)
    return LeadType(**lead.to_dict())

def resolve_update_lead(id: str, input: LeadInput) -> Optional[LeadType]:
    lead_data = {k: v for k, v in input.__dict__.items() if v is not None}
    lead = db.update(Lead, id, **lead_data)
    if lead:
        return LeadType(**lead.to_dict())
    return None

def resolve_delete_lead(id: str) -> bool:
    return db.delete(Lead, id)

def resolve_create_task(input: TaskInput) -> TaskType:
    task_data = input.__dict__.copy()
    task = db.create(Task, **task_data)

    # Create relationship with lead
    if input.lead_id:
        db.add_relationship(Task, task.id, 'lead', Lead, input.lead_id)

    return TaskType(**task.to_dict())

def resolve_update_task(id: str, input: TaskInput) -> Optional[TaskType]:
    task_data = {k: v for k, v in input.__dict__.items() if v is not None}
    task = db.update(Task, id, **task_data)
    if task:
        return TaskType(**task.to_dict())
    return None

def resolve_delete_task(id: str) -> bool:
    return db.delete(Task, id)

def resolve_create_note(input: NoteInput) -> NoteType:
    note_data = input.__dict__.copy()
    note = db.create(Note, **note_data)

    # Create relationships
    if input.lead_id:
        db.add_relationship(Note, note.id, 'lead', Lead, input.lead_id)
    if input.task_id:
        db.add_relationship(Note, note.id, 'task', Task, input.task_id)

    return NoteType(**note.to_dict())

def resolve_update_note(id: str, input: NoteInput) -> Optional[NoteType]:
    note_data = {k: v for k, v in input.__dict__.items() if v is not None}
    note = db.update(Note, id, **note_data)
    if note:
        return NoteType(**note.to_dict())
    return None

def resolve_delete_note(id: str) -> bool:
    return db.delete(Note, id)

def resolve_create_appointment(input: AppointmentInput) -> AppointmentType:
    appointment_data = input.__dict__.copy()
    appointment = db.create(Appointment, **appointment_data)

    # Create relationship with lead
    if input.lead_id:
        db.add_relationship(Appointment, appointment.id, 'lead', Lead, input.lead_id)

    return AppointmentType(**appointment.to_dict())

def resolve_update_appointment(id: str, input: AppointmentInput) -> Optional[AppointmentType]:
    appointment_data = {k: v for k, v in input.__dict__.items() if v is not None}
    appointment = db.update(Appointment, id, **appointment_data)
    if appointment:
        return AppointmentType(**appointment.to_dict())
    return None

def resolve_delete_appointment(id: str) -> bool:
    return db.delete(Appointment, id)

def resolve_create_vehicle(input: VehicleInput) -> VehicleType:
    vehicle_data = input.__dict__.copy()
    vehicle = db.create(Vehicle, **vehicle_data)

    # Create relationship with lead
    if input.lead_id:
        db.add_relationship(Vehicle, vehicle.id, 'lead', Lead, input.lead_id)

    return VehicleType(**vehicle.to_dict())

def resolve_update_vehicle(id: str, input: VehicleInput) -> Optional[VehicleType]:
    vehicle_data = {k: v for k, v in input.__dict__.items() if v is not None}
    vehicle = db.update(Vehicle, id, **vehicle_data)
    if vehicle:
        return VehicleType(**vehicle.to_dict())
    return None

def resolve_delete_vehicle(id: str) -> bool:
    return db.delete(Vehicle, id)

def resolve_get_all_tasks(page: int = 0, size: int = 10) -> dict:
    all_tasks = db.get_all(Task)
    tasks_data = [TaskType(**task.to_dict()) for task in all_tasks]
    result = paginate(tasks_data, page, size)
    return {
        'items': result['items'],
        'page_info': {
            'total': result['page_info']['total'],
            'page': result['page_info']['page'],
            'size': result['page_info']['size'],
            'has_next': result['page_info']['has_next'],
            'has_previous': result['page_info'].get('has_previous', False)
        }
    }


def resolve_get_lead_status_counts() -> List[LeadStatusCount]:
    from .types import LeadStatus  # Import here to avoid circular imports
    from collections import defaultdict

    # Get all leads
    all_leads = db.get_all(Lead)

    # Initialize counts for all statuses
    status_counts = defaultdict(int)
    for status in LeadStatus:
        status_counts[status.value] = 0

    # Count leads per status
    for lead in all_leads:
        status = lead.to_dict().get('lead_status')
        if status in status_counts:
            status_counts[status] += 1

    # Convert to list of LeadStatusCount objects
    return [
        LeadStatusCount(status=status, count=count)
        for status, count in status_counts.items()
    ]