from app.database.repositories.repository import Repository
from app.modules.worker.models.worker import Worker

class WorkerRepository(Repository):
    
    repository:Repository

    def __init__(self):
       self.repository = super()
       self.repository.__init__('workers',Worker)