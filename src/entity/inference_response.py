class InferenceStatus():
    PENDING = 'PENDING'
    COMPLETED = 'COMPELETED'

class InferenceResponse():
    def __init__(self, uid, results):
        self.uid = uid
        self.results = results
        