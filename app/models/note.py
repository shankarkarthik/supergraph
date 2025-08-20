from typing import Optional
from .base import BaseModel


class Note(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title: str = kwargs['title']
        self.content: Optional[str] = kwargs.get('content')
        self.author: Optional[str] = kwargs.get('author')
        self.lead_id: Optional[str] = kwargs.get('lead_id')
        self.task_id: Optional[str] = kwargs.get('task_id')

        # Relationships
        self.lead: Optional['Lead'] = None
        self.task: Optional['Task'] = None

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'lead_id': self.lead_id,
            'task_id': self.task_id,
        })
        return data
