from django.db import models

class Endpoint(models.Model):
    '''
    Represents a route in the API.

    Attributes:
        name: the name of the endpoint as it will show in the URL
        owner: the name of the owner
        created_at: the date when this endpoint was created
    '''
    name = models.CharField(max_length=128)
    owner = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.name

class MLAlgorithm(models.Model):
    '''
    Represents an algorithm provided by the API for use in inference.

    Attributes:
        name: the name of this algorithm
        description: a short description of how this algorithm works
        code: the algorithm source code
        version: the version number of this algorithm
        owner: the name of the owner
        created_at: the date when this algorithm was added to the database
        parent_endpoint: a reference to the endpoint where this algorithm is provided
    '''
    name = models.CharField(max_length=128)
    description = models.TextField()
    code = models.TextField()
    version = models.CharField(max_length=128)
    owner = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    parent_endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)

    def __str__(self):
        str = f"{self.name} (v{self.version}) -- "
        if len(self.description) > 50:
            return f"{str}{self.description[:50]}..."
        else:
            return str + self.description

    class Meta:
        verbose_name = "ML algorithm"

class MLAlgorithmStatus(models.Model):
    '''
    Represents the status of an algorithm which may change over the course of development.

    Attributes:
        status: the status of the parent algorithm (includes: testing, staging, production, ab_testing)
        active: a boolean flag indicating if the current status is active
        created_by: the name of this status' creator
        created_at: the date this status was created
        parent_mlalgorithm: a reference to the associated MLAlgorithm

    '''
    status = models.CharField(max_length=16)
    active = models.BooleanField()
    created_by = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_mlalgorithm = models.ForeignKey(MLAlgorithm, 
                                            on_delete=models.CASCADE, 
                                            related_name = "status", 
                                            verbose_name="parent ML algorithm")

    def __str__(self):
        return f"{self.parent_mlalgorithm.name} (v{self.parent_mlalgorithm.version}).{self.status}"

    class Meta:
        verbose_name = "ML algorithm status"
        verbose_name_plural = "ML algorithm statuses"
        
class MLRequest(models.Model):
    '''
    An object that holds information about a request to an associated MLAlgorithm.

    Attributes:
        input_data: input data sent to the algorithm in JSON format
        full_response: the response returned to the request from the algorithm
        response: the response from the algorithm in JSON format
        feedback: feedback about the response in JSON format
        created_at: the date when this request was created
        parent_mlalgorithm: a reference to a MLAlgorithm objct used to create the response
    '''
    input_data = models.TextField(max_length=10000)
    full_response = models.TextField(max_length=10000)
    response = models.TextField(max_length=10000)
    feedback = models.TextField(max_length=10000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    parent_mlalgorithm = models.ForeignKey(MLAlgorithm, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "ML request"