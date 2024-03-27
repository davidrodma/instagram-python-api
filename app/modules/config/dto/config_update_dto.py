from .config_create_dto import ConfigCreateDto
from typing import Optional

class ConfigUpdateDto(ConfigCreateDto):
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None