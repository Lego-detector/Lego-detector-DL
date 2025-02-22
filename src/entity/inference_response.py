class InferenceStatus():
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'

class InferenceResponse():
    def __init__(self, uid, results, delivery_tag, status=InferenceStatus.COMPLETED):
        self.uid = uid
        self.delivery_tag = delivery_tag
        self.results = results
        self.status = status
        