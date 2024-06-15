from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

# Define a type variable
T = TypeVar("T")


# Define the generic model
class GenericResponseDTO(BaseModel, Generic[T]):
    result: bool
    data: Optional[T]
    message: Optional[str]
