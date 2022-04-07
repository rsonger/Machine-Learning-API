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

try:
    registry = MLRegistry()
    rf = IncomeClassifier("random_forest.joblib")
    et = IncomeClassifier("extra_trees.joblib")

    registry.add_algorithm(endpoint_name="income_classifier_rf",
                           algorithm_object=rf,
                           algorithm_name="Random Forest",
                           algorithm_status="production",
                           algorithm_version="0.0.1",
                           owner="Rob",
                           algorithm_description="Random Forest for classifying income as above or below 50K.",
                           algorithm_code=inspect.getsource(IncomeClassifier))
    
    registry.add_algorithm(endpoint_name="income_classifier_et",
                           algorithm_object=et,
                           algorithm_name="Extra Trees",
                           algorithm_status="production",
                           algorithm_version="0.0.1",
                           owner="Rob",
                           algorithm_description="Extra Trees for classifying income as above or below 50K.",
                           algorithm_code=inspect.getsource(IncomeClassifier))
    
except Exception as e:
    print(f"Exception while loading algorithms to the registry:\n>>\t{str(e)}")