from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4, UUID


class BaseModel:
    def __init__(self, **kwargs):
        self.id: str = str(kwargs.get('id', str(uuid4())))
        self.created_at: str = kwargs.get('created_at', datetime.utcnow().isoformat())
        self.updated_at: str = kwargs.get('updated_at', datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    def update(self, **kwargs) -> None:
        """Update model fields."""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow().isoformat()
