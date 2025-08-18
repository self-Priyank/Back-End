from pydantic import BaseModel, Field
from typing import Optional

class TASK(BaseModel):
    id: str
    task_title: str
    username: str
    task_description: str
    task_order: int = Field(gt=0, description="order value must be greater than 0")
    task_status: str = "pending"
    start_time: float
    deadline: Optional[float] = None
    completion_time: Optional[float] = None
    is_pinned: bool = False

class TASK_CREATE(BaseModel):
    task_title: str
    username: str
    task_description: str
    task_order: int = Field(gt=0, description="order value must be greater than 0")