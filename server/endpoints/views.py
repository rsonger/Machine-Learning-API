from django.db import transaction
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.exceptions import APIException

from .models import Endpoint
from .serializers import EndpointSerializer

from .models import MLAlgorithm
from .serializers import MLAlgorithmSerializer

from .models import MLAlgorithmStatus
from .serializers import MLAlgorithmStatusSerializer

from .models import MLRequest
from .serializers import MLRequestSerializer

# PredictView imports
import json
from numpy.random import rand
from rest_framework import views, status
from rest_framework.response import Response

# from ml.registry import MLRegistry
from server.wsgi import registry

class EndpointViewSet(
    mixins.RetrieveModelMixin, 
    mixins.ListModelMixin, 
    viewsets.GenericViewSet
):
    """
    A read-only view for a single Endpoint or a list of Endpoints.
    """
    serializer_class = EndpointSerializer
    queryset = Endpoint.objects.all()


class MLAlgorithmViewSet(
    mixins.RetrieveModelMixin, 
    mixins.ListModelMixin, 
    viewsets.GenericViewSet
):
    """
    A read-only view for a single ML algorithm or a list of ML algorithms.
    """
    serializer_class = MLAlgorithmSerializer
    queryset = MLAlgorithm.objects.all()


def deactivate_other_statuses(instance):
    old_statuses = MLAlgorithmStatus.objects.filter(
        parent_mlalgorithm = instance.parent_mlalgorithm,
        created_at__lt=instance.created_at,
        active=True
    )
    for status in old_statuses:
        status.active = False
    MLAlgorithmStatus.objects.bulk_update(old_statuses, ["active"])

class MLAlgorithmStatusViewSet(
    mixins.RetrieveModelMixin, 
    mixins.ListModelMixin, 
    viewsets.GenericViewSet,
    mixins.CreateModelMixin
):
    """
    A view for a single ML algorithm status or a list of ML algorithm statuses.
    Statuses can be created but not edited.
    """
    serializer_class = MLAlgorithmStatusSerializer
    queryset = MLAlgorithmStatus.objects.all()
    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                instance = serializer.save(active=True)
                # set active=False for other statuses
                deactivate_other_statuses(instance)
        except Exception as e:
            raise APIException(str(e))

class MLRequestViewSet(
    mixins.RetrieveModelMixin, 
    mixins.ListModelMixin, 
    viewsets.GenericViewSet,
    mixins.UpdateModelMixin
):
    """
    A view for a single ML request or a list of ML requests.
    Only the feedback field may be updated due to the restrictions defined
    in the MLRequestSerializer.
    """
    serializer_class = MLRequestSerializer
    queryset = MLRequest.objects.all()

class PredictView(views.APIView):
    """
    A view for returning the prediction result of an endpoint.
    """
    def post(self, request, endpoint_name, format=None):

        algorithm_status = self.request.query_params.get("status", 
                                                         "production")
        algorithm_version = self.request.query_params.get("version")

        db_objs = MLAlgorithm.objects.filter(
            parent_endpoint__name = endpoint_name, 
            status__status = algorithm_status, 
            status__active=True
        )

        if algorithm_version is not None:
            db_objs = db_objs.filter(version = algorithm_version)

        if len(db_objs) == 0:
            return Response(
                {
                    "status": "Error", 
                    "message": "ML algorithm is not available"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(db_objs) != 1 and algorithm_status != "ab_testing":
            return Response(
                {
                    "status": "Error", 
                    "message": "ML algorithm selection is ambiguous. Please specify algorithm version."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        algo_index = 0

        if algorithm_status == "ab_testing":
            algo_index = round(rand())

        # use the algorithm and to make a prediction
        algorithm_object = registry.get_algorithm(db_objs[algo_index].id)
        if algorithm_object is not None:
            prediction = algorithm_object.compute_prediction(request.data)
        else:
            prediction = {"status": "Error", "message": "Unable to find algorithm in registry."}

        # Log the request-response in a MLRequest object
        ml_request = MLRequest(
            input_data=json.dumps(request.data),
            full_response=prediction,
            response=prediction["status"],
            feedback="",
            parent_mlalgorithm=db_objs[algo_index],
        )
        ml_request.save()

        prediction["request_id"] = ml_request.id

        return Response(prediction)