from endpoints.models import Endpoint
from endpoints.models import MLAlgorithm
from endpoints.models import MLAlgorithmStatus
from ml.income_classifier.income_classifier import IncomeClassifier

class MLRegistry:
    def __init__(self):
        self.__endpoint_algorithms = {}

        for algorithm in MLAlgorithm.objects.all():
            if algorithm.parent_endpoint.name == "income_classifier":
                algo_object = IncomeClassifier(algorithm.name)
            else:
                raise Exception(f"Unknown endpoint for algorithm {algorithm.id}: {algorithm.parent_endpoint.name}")
            self.register_algorithm(algorithm.id, algo_object)

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

        self.register_algorithm(db_object.id, algorithm_object)
        return db_object.id

    def register_algorithm(self, db_id, algorithm_object):
        """
        Add to the algorithm object to the registry dictionary and 
        associate it with its corresponding DB object ID.
        """
        if not MLAlgorithm.objects.filter(id=db_id).exists():
            raise Exception(f"Algorithm (id={db_id}) is not registered in the database.")
        self.__endpoint_algorithms[db_id] = algorithm_object

    def is_registered(self, endpoint_name, algorithm_name, 
                      algorithm_version, algorithm_status):
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

    def __len__(self):
        return len(self.__endpoint_algorithms)