from pydantic import BaseModel

class WorkerDisableDto(BaseModel):
    username: str
    reason: str = ''