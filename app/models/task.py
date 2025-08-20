from datetime import datetime
from typing import List, Optional
from .base import BaseModel


class Task(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title: str = kwargs['title']
        self.description: Optional[str] = kwargs.get('description')
        self.due_date: str = kwargs['due_date']
        self.status: str = kwargs.get('status', 'PENDING')
        self.priority: str = kwargs.get('priority', 'MEDIUM')
        self.assignee: str = kwargs['assignee']
        self.lead_id: str = kwargs['lead_id']

        # Relationships
        self.notes: List['Note'] = []
        self.lead: Optional['Lead'] = None

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'status': self.status,
            'priority': self.priority,
            'assignee': self.assignee,
            'lead_id': self.lead_id,
        })
        return data
