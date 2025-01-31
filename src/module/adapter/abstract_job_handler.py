from abc import ABC, abstractmethod
from entity import Job, InferenceResponse

class AbstractJobHandler(ABC):
    @abstractmethod
    def get_job(self) -> Job:
        raise NotImplementedError()
    
    @abstractmethod
    def mark_job_as_done(self, results: InferenceResponse) -> None:
        raise NotImplementedError()



        