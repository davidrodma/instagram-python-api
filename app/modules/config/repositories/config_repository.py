from app.database.repositories.repository import Repository
from app.modules.config.models.config import Config

class ConfigRepository(Repository):
    
    repository:Repository

    def __init__(self):
       self.repository = super()
       self.repository.__init__('configs',Config)