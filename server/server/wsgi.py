"""
WSGI config for server project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

application = get_wsgi_application()


# ML registry
import inspect
from ml.registry import MLRegistry
from ml.income_classifier.income_classifier import IncomeClassifier

# try:
registry = MLRegistry()
rf = IncomeClassifier("random_forest.joblib")
et = IncomeClassifier("extra_trees.joblib")

algos_to_add = (
    {
        "endpoint": "income_classifier",
        "name": "Random Forest",
        "version": "0.0.1"
    },
    # {
    #     "endpoint": "income_classifier",
    #     "name": "Extra Trees",
    #     "version": "0.0.1"
    # }
)

for algo in algos_to_add:
    print(f"Checking algorithm\n\t{algo}")
    # if not registry.is_registered(algo["endpoint"], algo["name"], algo["version"]):
    registry.add_algorithm(endpoint_name=algo["endpoint"],
                        algorithm_object=rf,
                        algorithm_name=algo["name"],
                        algorithm_status="production",
                        algorithm_version=algo["version"],
                        owner="Rob",
                        algorithm_description="Classifier model for predicting income as above or below 50K.",
                        algorithm_code=inspect.getsource(IncomeClassifier))
    
# except Exception as e:
    # print(f"Exception while loading algorithms to the registry:\n>>\t{type(e)} :: {e}")

print(f"-> Finished initializing registry:\n>>\t{registry}")