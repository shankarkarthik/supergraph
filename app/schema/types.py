from datetime import datetime
from enum import Enum
from typing import List, Optional
import strawberry
from strawberry.scalars import JSON
# Add these imports at the top of types.py
from typing import TYPE_CHECKING, List, Optional
import strawberry
from strawberry.scalars import JSON

if TYPE_CHECKING:
    from .resolvers import (
        resolve_lead_tasks,
        resolve_lead_vehicles,
        resolve_lead_notes,
        resolve_lead_appointments,
        resolve_task_lead,
        resolve_task_notes,
        resolve_note_lead,
        resolve_note_task,
        resolve_appointment_lead,
        resolve_appointment_notes,
        resolve_vehicle_lead
    )
# Enums
@strawberry.enum
class SortOrder(Enum):
    ASC = "ASC"
    DESC = "DESC"

@strawberry.enum
class VehicleSortField(Enum):
    MAKE = "MAKE"
    MODEL = "MODEL"
    YEAR = "YEAR"
    MILEAGE = "MILEAGE"
    CREATED_AT = "CREATED_AT"
    UPDATED_AT = "UPDATED_AT"

@strawberry.enum
class AppointmentSortField(Enum):
    TITLE = "TITLE"
    START_TIME = "START_TIME"
    END_TIME = "END_TIME"
    CREATED_AT = "CREATED_AT"
    UPDATED_AT = "UPDATED_AT"

@strawberry.enum
class TaskStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

@strawberry.enum
class TaskPriority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

@strawberry.enum
class LeadStatus(Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    UNQUALIFIED = "UNQUALIFIED"
    CUSTOMER = "CUSTOMER"

@strawberry.enum
class AppointmentStatus(Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"

@strawberry.enum
class VehicleCondition(Enum):
    NEW = "NEW"
    USED = "USED"
    CERTIFIED_PREOWNED = "CERTIFIED_PREOWNED"
    LEMON = "LEMON"
    SALVAGE = "SALVAGE"

# Input Types
@strawberry.input
class StringFilterInput:
    eq: Optional[str] = None
    ne: Optional[str] = None
    contains: Optional[str] = None
    not_contains: Optional[str] = None
    in_list: Optional[List[str]] = None
    not_in: Optional[List[str]] = None
    starts_with: Optional[str] = None
    ends_with: Optional[str] = None

@strawberry.input
class IntFilterInput:
    eq: Optional[int] = None
    ne: Optional[int] = None
    gt: Optional[int] = None
    lt: Optional[int] = None
    gte: Optional[int] = None
    lte: Optional[int] = None
    in_list: Optional[List[int]] = None
    not_in: Optional[List[int]] = None

@strawberry.input
class TimeRangeInput:
    eq: Optional[str] = None
    ne: Optional[str] = None
    gt: Optional[str] = None
    lt: Optional[str] = None
    gte: Optional[str] = None
    lte: Optional[str] = None
    between: Optional[List[str]] = None

@strawberry.input
class VehicleFilterInput:
    make: Optional[StringFilterInput] = None
    model: Optional[StringFilterInput] = None
    year: Optional[StringFilterInput] = None
    condition: Optional[StringFilterInput] = None

@strawberry.input
class AppointmentFilterInput:
    title: Optional[str] = None
    status: Optional[str] = None
    lead_id: Optional[str] = None
    start_time: Optional[TimeRangeInput] = None

# Input Types for Mutations
@strawberry.input
class LeadInput:
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    lead_source: Optional[str] = None
    lead_status: Optional[LeadStatus] = LeadStatus.NEW
    lead_owner: Optional[str] = None
    lead_stage: Optional[str] = None
    lead_score: Optional[int] = None
    lead_description: Optional[str] = None
    lead_notes: Optional[str] = None
    lead_type: Optional[str] = None

@strawberry.input
class TaskInput:
    title: str
    description: Optional[str] = None
    due_date: str
    status: Optional[TaskStatus] = TaskStatus.PENDING
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    assignee: str
    lead_id: str

@strawberry.input
class NoteInput:
    title: str
    content: Optional[str] = None
    author: Optional[str] = None
    lead_id: Optional[str] = None
    task_id: Optional[str] = None

@strawberry.input
class AppointmentInput:
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: str
    end_time: str
    status: Optional[AppointmentStatus] = AppointmentStatus.SCHEDULED
    reminder_time: Optional[str] = None
    lead_id: str

@strawberry.input
class VehicleInput:
    make: str
    model: Optional[str] = None
    year: str
    color: Optional[str] = None
    vin: Optional[str] = None
    license_plate: Optional[str] = None
    mileage: Optional[int] = None
    condition: Optional[VehicleCondition] = None
    notes: Optional[str] = None
    lead_id: str

# Pagination Types
@strawberry.type
class PageInfo:
    total: int
    page: int
    size: int
    has_next: bool
    has_previous: bool = False

@strawberry.type
class LeadPaginationResult:
    items: List["LeadType"]
    page_info: PageInfo

@strawberry.type
class AppointmentPaginationResult:
    items: List["AppointmentType"]
    page_info: PageInfo

# Regular Types
@strawberry.type
class VehicleType:
    id: str
    make: str
    model: Optional[str]
    year: str
    color: Optional[str]
    vin: Optional[str]
    license_plate: Optional[str]
    mileage: Optional[int]
    condition: Optional[str]
    notes: Optional[str]
    lead_id: str
    created_at: str
    updated_at: str

    @strawberry.field
    def lead(self) -> Optional["LeadType"]:
        # This will be resolved by the resolver
        pass

@strawberry.type
class TaskType:
    id: str
    title: str
    description: Optional[str]
    due_date: str
    status: str
    priority: str
    assignee: str
    lead_id: str
    created_at: str
    updated_at: str

    @strawberry.field
    def lead(self) -> Optional["LeadType"]:
        # This will be resolved by the resolver
        pass

    @strawberry.field
    def notes(self) -> List["NoteType"]:
        # This will be resolved by the resolver
        return []

@strawberry.type
class NoteType:
    id: str
    title: str
    content: Optional[str]
    author: Optional[str]
    lead_id: Optional[str]
    task_id: Optional[str]
    created_at: str
    updated_at: str

    @strawberry.field
    def lead(self) -> Optional["LeadType"]:
        # This will be resolved by the resolver
        pass

    @strawberry.field
    def task(self) -> Optional[TaskType]:
        # This will be resolved by the resolver
        pass

@strawberry.type
class AppointmentType:
    id: str
    title: str
    description: Optional[str]
    location: Optional[str]
    start_time: str
    end_time: str
    status: str
    reminder_time: Optional[str]
    lead_id: str
    created_at: str
    updated_at: str

    @strawberry.field
    def lead(self) -> Optional["LeadType"]:
        # This will be resolved by the resolver
        pass

    @strawberry.field
    def notes(self) -> List[NoteType]:
        # This will be resolved by the resolver
        return []

@strawberry.type
class LeadType:
    id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip: Optional[str]
    lead_source: Optional[str]
    lead_status: str
    lead_owner: Optional[str]
    lead_stage: Optional[str]
    lead_score: Optional[int]
    lead_description: Optional[str]
    lead_notes: Optional[str]
    lead_type: Optional[str]
    created_at: str
    updated_at: str

    @strawberry.field
    def tasks(self) -> "List[TaskType]":
        from .resolvers import resolve_lead_tasks
        return resolve_lead_tasks(self)

    @strawberry.field
    def vehicles(self, filter: Optional[VehicleFilterInput] = None) -> "List[VehicleType]":
        from .resolvers import resolve_lead_vehicles
        return resolve_lead_vehicles(self, filter)

    @strawberry.field
    def notes(self) -> "List[NoteType]":
        from .resolvers import resolve_lead_notes
        return resolve_lead_notes(self)

    @strawberry.field
    def appointments(self) -> "List[AppointmentType]":
        from .resolvers import resolve_lead_appointments
        return resolve_lead_appointments(self)

@strawberry.type
class TaskPaginationResult:
    items: List["TaskType"]
    page_info: "PageInfo"
