from typing import Dict, List, TypeVar, Type, Any, Optional
from datetime import datetime
from uuid import uuid4

T = TypeVar('T')

class InMemoryDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InMemoryDB, cls).__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        self._data: Dict[type, Dict[str, Any]] = {
            'Lead': {},
            'Task': {},
            'Note': {},
            'Appointment': {},
            'Vehicle': {}
        }
        self._relationships = {
            'Lead': {
                'tasks': [],
                'vehicles': [],
                'notes': [],
                'appointments': []
            },
            'Task': {
                'notes': [],
                'lead': {}
            },
            'Note': {
                'lead': {},
                'task': {}
            },
            'Appointment': {
                'lead': {},
                'notes': []
            },
            'Vehicle': {
                'lead': {}
            }
        }

    def create(self, model_type: Type[T], **data) -> T:
        if 'id' not in data:
            data['id'] = str(uuid4())

        now = datetime.utcnow().isoformat()
        if 'created_at' not in data:
            data['created_at'] = now
        if 'updated_at' not in data:
            data['updated_at'] = now

        model = model_type(**data)
        self._data[model_type.__name__][data['id']] = model
        return model

    def get(self, model_type: Type[T], id: str) -> Optional[T]:
        return self._data[model_type.__name__].get(id)

    def get_all(self, model_type: Type[T]) -> List[T]:
        return list(self._data[model_type.__name__].values())

    def update(self, model_type: Type[T], id: str, **data) -> Optional[T]:
        if id not in self._data[model_type.__name__]:
            return None

        # Don't update id, created_at
        data.pop('id', None)
        data.pop('created_at', None)

        model = self._data[model_type.__name__][id]
        model.update(**data)
        return model

    def delete(self, model_type: Type[T], id: str) -> bool:
        if id in self._data[model_type.__name__]:
            # Clean up relationships
            model_name = model_type.__name__
            if model_name in self._relationships:
                # Remove from all relationships
                for rel_name, rel_data in self._relationships[model_name].items():
                    if isinstance(rel_data, list):
                        # Many-to-many or one-to-many relationship
                        rel_data = [r for r in rel_data if r[0] != id]
                        self._relationships[model_name][rel_name] = rel_data
                    elif isinstance(rel_data, dict):
                        # One-to-one relationship
                        rel_data.pop(id, None)

            # Delete the model
            del self._data[model_type.__name__][id]
            return True
        return False

    def add_relationship(self, from_model_type: Type[T], from_id: str,
                        rel_name: str, to_model_type: Type[T], to_id: str) -> bool:
        from_model_name = from_model_type.__name__
        to_model_name = to_model_type.__name__

        # Check if both models exist
        if (from_id not in self._data[from_model_name] or
            to_id not in self._data[to_model_name]):
            return False

        # Initialize relationship if it doesn't exist
        if from_model_name not in self._relationships:
            self._relationships[from_model_name] = {}
        if rel_name not in self._relationships[from_model_name]:
            self._relationships[from_model_name][rel_name] = []

        # Add relationship
        self._relationships[from_model_name].setdefault(rel_name, []).append((from_id, to_id))
        return True

    def get_related(self, model_type: Type[T], id: str, rel_name: str) -> List[Any]:
        model_name = model_type.__name__
        if (model_name not in self._relationships or
            rel_name not in self._relationships[model_name]):
            return []

        related_ids = [r[1] for r in self._relationships[model_name][rel_name] if r[0] == id]
        related_models = []

        # Find the related model type (this is a simplification)
        related_type = None
        if rel_name == 'tasks':
            from .models.task import Task
            related_type = Task
        elif rel_name == 'vehicles':
            from .models.vehicle import Vehicle
            related_type = Vehicle
        elif rel_name == 'notes':
            from .models.note import Note
            related_type = Note
        elif rel_name == 'appointments':
            from .models.appointment import Appointment
            related_type = Appointment

        if related_type:
            related_models = [self.get(related_type, rid) for rid in related_ids]
            return [m for m in related_models if m is not None]

        return []

    def get_related_single(self, model_type: Type[T], id: str, rel_name: str) -> Any:
        model_name = model_type.__name__
        if (model_name not in self._relationships or
            rel_name not in self._relationships[model_name]):
            return None

        related_id = self._relationships[model_name][rel_name].get(id)
        if not related_id:
            return None

        # Find the related model type (this is a simplification)
        related_type = None
        if rel_name == 'lead':
            from .models.lead import Lead
            related_type = Lead
        elif rel_name == 'task':
            from .models.task import Task
            related_type = Task

        if related_type:
            return self.get(related_type, related_id)

        return None

    def clear(self):
        """Clear all data (for testing purposes)"""
        self._init_db()

# Create a singleton instance
db = InMemoryDB()
