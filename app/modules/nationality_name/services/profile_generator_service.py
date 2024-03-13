from faker import Faker
import random
import string
from app.modules.nationality_name.services.nationality_name_service import NationalityNameService
from app.modules.nationality_name.types.simple_profile_generated_type import SimpleProfileGenerated
from app.modules.nationality_name.types.name_gender_nationality_generated_type import NameGenderNationalityGenerated

class ProfileGeneratorService:
    def __init__(self):
        self.faker = Faker()
        self.nationality_name_service = NationalityNameService()

    @classmethod
    def username(self,length=20):
        characters = 'abcdefghijklmnopqrstuvwxyz0123456789_.'
        username = ''.join(random.choice(characters) for _ in range(length))
        return username.lower()
    
    @classmethod
    def password(self, length=10, pool=string.ascii_letters + string.digits + string.punctuation):
        return ''.join(random.choices(pool, k=length))

    @classmethod
    def full_name(self):
        return self.faker.name()

    @classmethod
    def birth(self):
        # Gerar uma data de nascimento aleatória entre 18 e 60 anos atrás
        dob = self.faker.date_of_birth(minimum_age=18, maximum_age=60)  # Inverso para garantir que a idade esteja no intervalo
        return {
            'day': dob.day,
            'month': dob.month,
            'year': dob.year
        }
    
    @classmethod
    def generate_simple(self)->SimpleProfileGenerated:
        fields = {
            "username":self.username(),
            "password":self.password(),
            "full_name":self.full_name(),
            "birth":self.birth()
        }
        return SimpleProfileGenerated(**fields)
    
    @classmethod
    def generate_by_gender_nationality(self,gender:str='female', nationality:str='')->NameGenderNationalityGenerated:
        return self.nationality_name_service.generate(gender,nationality)
        