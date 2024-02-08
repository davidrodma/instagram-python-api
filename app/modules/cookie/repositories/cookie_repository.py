from app.database.repositories.repository import Repository
from app.modules.cookie.models.cookie import Cookie

class CookieRepository(Repository):
    
    repository:Repository

    def __init__(self):
       self.repository = super()
       self.repository.__init__('cookies',Cookie)