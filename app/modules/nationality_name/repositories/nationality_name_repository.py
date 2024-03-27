from app.database.repositories.repository import Repository
from app.modules.nationality_name.models.nationality_name import NationalityName

class NationalityNameRepository(Repository):
    
    repository:Repository

    def __init__(self):
       self.repository = super()
       self.repository.__init__('nationalitynames',NationalityName)