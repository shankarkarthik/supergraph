import strawberry
from typing import List, Optional
from .types import (
    LeadType, TaskType, NoteType, AppointmentType, VehicleType,
    LeadInput, TaskInput, NoteInput, AppointmentInput, VehicleInput,
    LeadPaginationResult, TaskPaginationResult, AppointmentPaginationResult, PageInfo,
    VehicleFilterInput, AppointmentFilterInput, SortOrder, AppointmentSortField, VehicleSortField
)
from .resolvers import (
    # Query resolvers
    resolve_get_lead, resolve_get_all_leads, resolve_get_leads_by_status,
    resolve_get_task, resolve_get_all_tasks, resolve_get_tasks_by_lead,
    resolve_get_note, resolve_get_notes_by_lead, resolve_get_notes_by_task,
    resolve_get_appointment, resolve_get_all_appointments,
    resolve_get_vehicle, resolve_get_vehicles_by_lead, resolve_get_vehicles,

    # Mutation resolvers
    resolve_create_lead, resolve_update_lead, resolve_delete_lead,
    resolve_create_task, resolve_update_task, resolve_delete_task,
    resolve_create_note, resolve_update_note, resolve_delete_note,
    resolve_create_appointment, resolve_update_appointment, resolve_delete_appointment,
    resolve_create_vehicle, resolve_update_vehicle, resolve_delete_vehicle,

    # Field resolvers
    resolve_lead_tasks, resolve_lead_vehicles, resolve_lead_notes, resolve_lead_appointments,
    resolve_task_lead, resolve_task_notes,
    resolve_note_lead, resolve_note_task,
    resolve_appointment_lead, resolve_appointment_notes,
    resolve_vehicle_lead
)

@strawberry.type
class Query:
    @strawberry.field
    def getLead(self, id: str) -> Optional[LeadType]:
        return resolve_get_lead(id)

    @strawberry.field
    def getAllLeads(self, page: int = 0, size: int = 10) -> LeadPaginationResult:
        return resolve_get_all_leads(page, size)

    @strawberry.field
    def getLeadsByStatus(self, status: str) -> LeadPaginationResult:
        return resolve_get_leads_by_status(status)

    @strawberry.field
    def getTask(self, id: str) -> Optional[TaskType]:
        return resolve_get_task(id)

    @strawberry.field
    def getAllTasks(self, page: int = 0, size: int = 10) -> TaskPaginationResult:
        result = resolve_get_all_tasks(page, size)
        return TaskPaginationResult(
            items=result['items'],
            page_info=PageInfo(**result['page_info'])
        )

    @strawberry.field
    def getTasksByLead(self, lead_id: str) -> List[TaskType]:
        return resolve_get_tasks_by_lead(lead_id)

    @strawberry.field
    def getNote(self, id: str) -> Optional[NoteType]:
        return resolve_get_note(id)

    @strawberry.field
    def getNotesByLead(self, lead_id: str) -> List[NoteType]:
        return resolve_get_notes_by_lead(lead_id)

    @strawberry.field
    def getNotesByTask(self, task_id: str) -> List[NoteType]:
        return resolve_get_notes_by_task(task_id)

    @strawberry.field
    def getAppointment(self, id: str) -> Optional[AppointmentType]:
        return resolve_get_appointment(id)

    @strawberry.field
    def getAllAppointments(
        self, 
        page: int = 0, 
        size: int = 10, 
        sort_by: str = "START_TIME", 
        sort_order: str = "DESC",
        filter: Optional[AppointmentFilterInput] = None
    ) -> AppointmentPaginationResult:
        return resolve_get_all_appointments(page, size, sort_by, sort_order, filter)

    @strawberry.field
    def getVehicle(self, id: str) -> Optional[VehicleType]:
        return resolve_get_vehicle(id)

    @strawberry.field
    def getVehiclesByLead(self, lead_id: str) -> List[VehicleType]:
        return resolve_get_vehicles_by_lead(lead_id)

    @strawberry.field
    def getVehicles(
        self, 
        filter: Optional[VehicleFilterInput] = None,
        sort_by: str = "CREATED_AT",
        sort_order: str = "DESC"
    ) -> List[VehicleType]:
        return resolve_get_vehicles(filter, sort_by, sort_order)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def createLead(self, input: LeadInput) -> LeadType:
        return resolve_create_lead(input)

    @strawberry.mutation
    def updateLead(self, id: str, input: LeadInput) -> Optional[LeadType]:
        return resolve_update_lead(id, input)

    @strawberry.mutation
    def deleteLead(self, id: str) -> bool:
        return resolve_delete_lead(id)

    @strawberry.mutation
    def createTask(self, input: TaskInput) -> TaskType:
        return resolve_create_task(input)

    @strawberry.mutation
    def updateTask(self, id: str, input: TaskInput) -> Optional[TaskType]:
        return resolve_update_task(id, input)

    @strawberry.mutation
    def deleteTask(self, id: str) -> bool:
        return resolve_delete_task(id)

    @strawberry.mutation
    def createNote(self, input: NoteInput) -> NoteType:
        return resolve_create_note(input)

    @strawberry.mutation
    def updateNote(self, id: str, input: NoteInput) -> Optional[NoteType]:
        return resolve_update_note(id, input)

    @strawberry.mutation
    def deleteNote(self, id: str) -> bool:
        return resolve_delete_note(id)

    @strawberry.mutation
    def createAppointment(self, input: AppointmentInput) -> AppointmentType:
        return resolve_create_appointment(input)

    @strawberry.mutation
    def updateAppointment(self, id: str, input: AppointmentInput) -> Optional[AppointmentType]:
        return resolve_update_appointment(id, input)

    @strawberry.mutation
    def deleteAppointment(self, id: str) -> bool:
        return resolve_delete_appointment(id)

    @strawberry.mutation
    def createVehicle(self, input: VehicleInput) -> VehicleType:
        return resolve_create_vehicle(input)

    @strawberry.mutation
    def updateVehicle(self, id: str, input: VehicleInput) -> Optional[VehicleType]:
        return resolve_update_vehicle(id, input)

    @strawberry.mutation
    def deleteVehicle(self, id: str) -> bool:
        return resolve_delete_vehicle(id)

# Create the schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
print(schema)