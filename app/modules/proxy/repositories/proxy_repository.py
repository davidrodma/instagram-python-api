from app.database.repositories.repository import Repository
from app.modules.proxy.models.proxy import Proxy

class ProxyRepository(Repository):
    
    repository:Repository

    def __init__(self):
       self.repository = super()
       self.repository.__init__('proxies',Proxy)