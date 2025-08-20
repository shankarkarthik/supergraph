from typing import List, Optional
from .base import BaseModel


class Lead(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name: str = kwargs['name']
        self.email: Optional[str] = kwargs.get('email')
        self.phone: Optional[str] = kwargs.get('phone')
        self.address: Optional[str] = kwargs.get('address')
        self.city: Optional[str] = kwargs.get('city')
        self.state: Optional[str] = kwargs.get('state')
        self.zip: Optional[str] = kwargs.get('zip')
        self.lead_source: Optional[str] = kwargs.get('lead_source')
        self.lead_status: str = kwargs.get('lead_status', 'NEW')
        self.lead_owner: Optional[str] = kwargs.get('lead_owner')
        self.lead_stage: Optional[str] = kwargs.get('lead_stage')
        self.lead_score: Optional[int] = kwargs.get('lead_score')
        self.lead_description: Optional[str] = kwargs.get('lead_description')
        self.lead_notes: Optional[str] = kwargs.get('lead_notes')
        self.lead_type: Optional[str] = kwargs.get('lead_type')

        # Relationships (will be populated by resolvers)
        self.tasks: List['Task'] = []
        self.vehicles: List['Vehicle'] = []
        self.notes: List['Note'] = []
        self.appointments: List['Appointment'] = []

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip': self.zip,
            'lead_source': self.lead_source,
            'lead_status': self.lead_status,
            'lead_owner': self.lead_owner,
            'lead_stage': self.lead_stage,
            'lead_score': self.lead_score,
            'lead_description': self.lead_description,
            'lead_notes': self.lead_notes,
            'lead_type': self.lead_type,
        })
        return data
