from typing import List, Optional
from .base import BaseModel


class Appointment(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title: str = kwargs['title']
        self.description: Optional[str] = kwargs.get('description')
        self.location: Optional[str] = kwargs.get('location')
        self.start_time: str = kwargs['start_time']
        self.end_time: str = kwargs['end_time']
        self.status: str = kwargs.get('status', 'SCHEDULED')
        self.reminder_time: Optional[str] = kwargs.get('reminder_time')
        self.lead_id: str = kwargs['lead_id']

        # Relationships
        self.lead: Optional['Lead'] = None
        self.notes: List['Note'] = []

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'status': self.status,
            'reminder_time': self.reminder_time,
            'lead_id': self.lead_id,
        })
        return data
