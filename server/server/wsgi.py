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

algos_to_add = (
    {
        "endpoint": "income_classifier",
        "name": "Random Forest",
        "version": "0.0.1",
        "status": "production"
    },
    {
        "endpoint": "income_classifier",
        "name": "Random Forest",
        "version": "0.0.2",
        "status": "ab_testing"
    },
    {
        "endpoint": "income_classifier",
        "name": "Extra Trees",
        "version": "0.0.2",
        "status": "ab_testing"
    }
)

for algo in algos_to_add:
    if not registry.is_registered(algo["endpoint"], algo["name"], algo["version"], algo["status"]):
        algorithm_object = IncomeClassifier(algo["name"])
        registry.add_algorithm(endpoint_name=algo["endpoint"],
                        algorithm_object=algorithm_object,
                        algorithm_name=algo["name"],
                        algorithm_status=algo["status"],
                        algorithm_version=algo["version"],
                        owner="Rob",
                        algorithm_description="Classifier model for predicting income as above or below 50K.",
                        algorithm_code=inspect.getsource(IncomeClassifier))
    
# except Exception as e:
    # print(f"Exception while loading algorithms to the registry:\n>>\t{type(e)} :: {e}")