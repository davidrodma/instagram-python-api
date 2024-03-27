from .boost_create_dto import BoostCreateDto
from typing import  Optional

class BoostUpdateDto(BoostCreateDto):
    password: Optional[str] = None