from typing import TypeVar, Generic, Optional, Any, Dict, List
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json

T = TypeVar("T")


def serialize_object(obj: Any) -> Any:
    """Serialize any object to JSON-compatible format"""
    if obj is None:
        return None
    # Handle lists first
    elif isinstance(obj, (list, set, tuple)):
        return [serialize_object(item) for item in obj]
    # Handle SQLAlchemy models
    elif hasattr(obj, "__class__") and isinstance(obj.__class__, DeclarativeMeta):
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        return {
            k: serialize_object(v)
            for k, v in obj.__dict__.items()
            if not k.startswith("_")
        }
    # Handle dictionaries
    elif isinstance(obj, dict):
        return {k: serialize_object(v) for k, v in obj.items()}
    # Handle datetime
    elif isinstance(obj, datetime):
        return obj.isoformat()
    # Handle basic types
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    # Handle other objects
    return str(obj)


class ResponseSchema(BaseModel, Generic[T]):
    """Standard response schema"""

    result: Optional[T] = None
    status: int = 200
    message: str = "Success"

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}

    def dict(self, *args, **kwargs) -> Dict:
        """Override dict method to handle serialization"""
        d = super().dict(*args, **kwargs)
        d["result"] = serialize_object(self.result)
        return d

    @classmethod
    def success(cls, result: Any = None, message: str = "Success") -> "ResponseSchema":
        """Create a success response"""
        return cls(result=result, status=200, message=message)

    @classmethod
    def error(cls, status: int = 400, message: str = "Error") -> "ResponseSchema":
        """Create an error response"""
        return cls(result=None, status=status, message=message)
