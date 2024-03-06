from .worker_create_dto import WorkerCreateDto
from typing import  Optional

class WorkerUpdateDto(WorkerCreateDto):
    password: Optional[str] = None