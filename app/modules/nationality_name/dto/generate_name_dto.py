from pydantic import BaseModel

class GenerateNameDto(BaseModel):
    gender: str = 'female'
    nationality: str = ''