from app.database.repositories.repository import Repository
from app.modules.boost.models.boost import Boost

class BoostRepository(Repository):
    
    repository:Repository

    def __init__(self):
       self.repository = super()
       self.repository.__init__('boosts',Boost)