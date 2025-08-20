from typing import Optional
from .base import BaseModel


class Vehicle(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.make: str = kwargs['make']
        self.model: Optional[str] = kwargs.get('model')
        self.year: str = kwargs['year']
        self.color: Optional[str] = kwargs.get('color')
        self.vin: Optional[str] = kwargs.get('vin')
        self.license_plate: Optional[str] = kwargs.get('license_plate')
        self.mileage: Optional[int] = kwargs.get('mileage')
        self.condition: Optional[str] = kwargs.get('condition')
        self.notes: Optional[str] = kwargs.get('notes')
        self.lead_id: str = kwargs['lead_id']

        # Relationships
        self.lead: Optional['Lead'] = None

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'color': self.color,
            'vin': self.vin,
            'license_plate': self.license_plate,
            'mileage': self.mileage,
            'condition': self.condition,
            'notes': self.notes,
            'lead_id': self.lead_id,
        })
        return data
