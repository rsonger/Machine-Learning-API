# Serializers allow complex data such as querysets and model instances 
# to be converted to native Python datatypes that can then be easily 
# rendered into JSON, XML or other content types. Serializers also 
# provide deserialization, allowing parsed data to be converted back 
# into complex types, after first validating the incoming data.
#
# https://www.django-rest-framework.org/api-guide/serializers/

from rest_framework import serializers
from .models import Endpoint
from .models import MLAlgorithm
from .models import MLAlgorithmStatus
from .models import MLRequest
from .models import ABTest

class EndpointSerializer(serializers.ModelSerializer):

    class Meta:
        model = Endpoint
        read_only_fields = ("id", "name", "owner", "created_at")
        fields = read_only_fields


class MLAlgorithmSerializer(serializers.ModelSerializer):

    current_status = serializers.SerializerMethodField(read_only=True)

    def get_current_status(self, mlalgorithm):
        return MLAlgorithmStatus.objects.filter(
            parent_mlalgorithm=mlalgorithm
        ).latest('created_at').status

    class Meta:
        model = MLAlgorithm
        read_only_fields = ("id", "name", "description", "code",
                            "version", "owner", "created_at",
                            "parent_endpoint", "current_status")
        fields = read_only_fields

class MLAlgorithmStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLAlgorithmStatus
        read_only_fields = ("id", "active")
        fields = ("id", "active", "status", "created_by", "created_at",
                  "parent_mlalgorithm")

class MLRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLRequest
        read_only_fields = ("id", "input_data", "full_response",
                            "response", "prediction", "created_at", 
                            "parent_mlalgorithm")
        fields =  ("id", "input_data", "full_response", "response",
                   "prediction", "feedback", "created_at", 
                   "parent_mlalgorithm")

class ABTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ABTest
        read_only_fields = ("id", "ended_at", "created_at", "summary")
        fields = ("id", "title", "created_by", "created_at", "ended_at",
                  "summary", "algorithm_A", "algorithm_B")