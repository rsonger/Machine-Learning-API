from endpoints.models import Endpoint
from endpoints.models import MLAlgorithm
from endpoints.models import MLAlgorithmStatus

class MLRegistry:
    def __init__(self):
        self.__endpoint_algorithms = {}

    def add_algorithm(self, endpoint_name, algorithm_object, 
                      algorithm_name, algorithm_status, 
                      algorithm_version, owner, algorithm_description, 
                      algorithm_code):
        # get endpoint record from the database
        endpoint, _ = Endpoint.objects.get_or_create(name=endpoint_name,
                                                     owner=owner)

        # get algorithm record from the database
        db_object, created = MLAlgorithm.objects.get_or_create(
            name=algorithm_name,
            description=algorithm_description,
            code=algorithm_code,
            version=algorithm_version,
            owner=owner,
            parent_endpoint=endpoint
        )
        if created:
            status = MLAlgorithmStatus(status = algorithm_status,
                                       created_by = owner,
                                       parent_mlalgorithm = db_object,
                                       active = True)
            status.save()

        # add to the algorithm object to the registry dictionary and
        # associate it with its corresponding db object ID
        self.__endpoint_algorithms[db_object.id] = algorithm_object

    def is_registered(self, endpoint_name, algorithm_name, 
                      algorithm_version):
        db_objects = MLAlgorithm.objects.filter(
                        parent_endpoint__name=endpoint_name,
                        name=algorithm_name,
                        version=algorithm_version
                    )
        return (
                len(db_objects) > 0 and
                db_objects[0].id in self.__endpoint_algorithms.keys()
        )

    def get_algorithm(self, db_object_id):
        if db_object_id in self.__endpoint_algorithms.keys():
            return self.__endpoint_algorithms[db_object_id]
        else:
            return None

    def __str__(self):
        return str(self.__endpoint_algorithms)