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
    parent_mlalgorithm = models.ForeignKey(
        MLAlgorithm, 
        on_delete=models.CASCADE, 
        related_name = "status", 
        verbose_name="parent ML algorithm"
    )

    def __str__(self):
        algo_name = self.parent_mlalgorithm.name
        algo_version = self.parent_mlalgorithm.version
        active = "<<ACTIVE>>" if self.active else ""
        return f"{algo_name} (v{algo_version}).{self.status} {active}"

    class Meta:
        verbose_name = "ML algorithm status"
        verbose_name_plural = "ML algorithm statuses"
        
class MLRequest(models.Model):
    '''
    An object that holds information about a request to an associated MLAlgorithm.

    Attributes:
        input_data: input data sent to the algorithm in JSON format
        full_response: the response returned to the request from the algorithmin JSON format
        response: shorthand of the response status, e.g. "OK" or "ERROR
        prediction: a label representing the predicted result
        feedback: feedback for comparing actual result to prediction
        created_at: the date when this request was created
        parent_mlalgorithm: a reference to a MLAlgorithm objct used to create the response
    '''
    input_data = models.TextField()
    full_response = models.TextField()
    response = models.CharField(max_length=32)
    prediction = models.CharField(max_length=64, null=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    parent_mlalgorithm = models.ForeignKey(MLAlgorithm, 
                                           on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.parent_mlalgorithm.name} ({self.created_at})"

    class Meta:
        verbose_name = "ML request"

class ABTest(models.Model):
    """
    An information record about an A/B test.

    Attributes:
        title: The title of this test.
        created_by: The name of the person who created this test.
        created_at: The date and time of the test's creation.
        ended_at: The date and time of the test's completion.
        summary: A description of the test.
        algorithm_A: The first algorithm referencing a MLAlgorithm object.
        algorithm_B: The second algorithm referencing a MLAlgorithm object.
    """
    title = models.CharField(max_length=256)
    created_by = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    summary = models.TextField(blank=True)

    algorithm_A = models.ForeignKey(MLAlgorithm,
                                    on_delete=models.CASCADE,
                                    related_name="algorithm_A")
    algorithm_B = models.ForeignKey(MLAlgorithm,
                                    on_delete=models.CASCADE,
                                    related_name="algorithm_B")
    
    def __str__(self):
        blip = "A/B Test: "
        title = self.title if len(self.title) < 50 else f"{self.title[:50]}..."
        active = "<<ACTIVE>>" if not self.ended_at else ""
        return f"{blip}{title} {active}"

    class Meta:
        verbose_name = "A/B Test"