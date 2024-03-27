from .profile_create_dto import ProfileCreateDto
from typing import  Optional

class ProfileUpdateDto(ProfileCreateDto):
    password: Optional[str] = None