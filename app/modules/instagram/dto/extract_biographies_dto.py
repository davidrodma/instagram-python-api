from pydantic import BaseModel

class ExtractBiographiesDto(BaseModel):
    username: str
    quantity:int
    min_char:int = 0