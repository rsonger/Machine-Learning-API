"""
WSGI config for server project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
from random import Random

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

application = get_wsgi_application()


# ML registry
import inspect
from ml.registry import MLRegistry
from ml.income_classifier.random_forest import RandomForestClassifier

try:
    registry = MLRegistry()
    rf = RandomForestClassifier()

    registry.add_algorithm(endpoint_name="income_classifier",
                           algorithm_object=rf,
                           algorithm_name="Random Forest",
                           algorithm_status="production",
                           algorithm_version="0.0.1",
                           owner="Rob",
                           algorithm_description="Random Forest with simple pre- and post-processing.",
                           algorithm_code=inspect.getsource(RandomForestClassifier))
except Exception as e:
    print(f"Exception while loading algorithms to the registry:\n>>\t{str(e)}")