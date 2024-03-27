from app.database.repositories.repository import Repository
from app.modules.profile.models.profile import Profile

class ProfileRepository(Repository):
    
    repository:Repository

    def __init__(self):
       self.repository = super()
       self.repository.__init__('profiles',Profile)