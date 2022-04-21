from os import sep
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

from endpoints.models import ABTest
from endpoints.serializers import ABTestSerializer

# PredictView imports
import json
from numpy.random import rand
from rest_framework import views, status
from rest_framework.response import Response
from server.wsgi import registry

# ABTestStopView imports
import datetime
from django.db.models import F


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
        parent_mlalgorithm=instance.parent_mlalgorithm,
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
            prediction = algorithm_object.compute_prediction(json.loads(request.data))
        else:
            prediction = {"status": "Error", "message": "Unable to find algorithm in registry."}

        # Log the request-response in a MLRequest object
        ml_request = MLRequest(
            input_data=json.loads(request.data),
            full_response=prediction,
            response=prediction["status"],
            prediction=prediction["label"] or None,
            feedback="",
            parent_mlalgorithm=db_objs[algo_index],
        )
        ml_request.save()

        prediction["request_id"] = ml_request.id

        return Response(prediction)

class ABTestViewSet(
    mixins.RetrieveModelMixin, 
    mixins.ListModelMixin, 
    viewsets.GenericViewSet, 
    mixins.CreateModelMixin, 
    mixins.UpdateModelMixin
):
    """
    A view for creating new A/B Tests.
    This view assigns "ab_testing" status to the two algorithms under test.
    """
    serializer_class = ABTestSerializer
    queryset = ABTest.objects.all()

    def perform_create(self, serializer):
        # try:
        with transaction.atomic():
            instance = serializer.save()

            # update the status for the first algorithm
            status_A, _ = MLAlgorithmStatus.objects.get_or_create(
                status="ab_testing",
                created_by=instance.created_by,
                parent_mlalgorithm=instance.algorithm_A,
                active=True
            )
            # status_A.save()
            deactivate_other_statuses(status_A)

            # update the status for the second algorithm
            status_B, _ = MLAlgorithmStatus.objects.get_or_create(
                status="ab_testing",
                created_by=instance.created_by,
                parent_mlalgorithm=instance.algorithm_B,
                active=True
            )
            # status_B.save()
            deactivate_other_statuses(status_B)
            
        # except Exception as e:
        #   raise APIException(str(e))

class ABTestStopView(views.APIView):
    """
    A view for stopping a running A/B Test.
    This view computes the accuracy of each assocated algorithm.
    The algorithm with higher accuracy is set to "production" status 
    while the other is set to "testing".
    """
    def post(self, request, ab_test_id, format=None):
        # try:
        ab_test = ABTest.objects.get(pk=ab_test_id)

        if ab_test.ended_at is not None:
            return Response({
                "message": "The specified A/B Test is already finished."
            })

        date_now = datetime.datetime.now()
        
        # calculate algorithm A accuracy
        responses_A = MLRequest.objects.filter(
            parent_mlalgorithm=ab_test.algorithm_A, 
            created_at__gt=ab_test.created_at, 
            created_at__lt=date_now
        ).count()
        correct_responses_A = MLRequest.objects.filter(
            parent_mlalgorithm=ab_test.algorithm_A, 
            created_at__gt=ab_test.created_at, 
            created_at__lt=date_now, 
            prediction=F('feedback')
        ).count()
        accuracy_A = correct_responses_A / float(responses_A)
        print(responses_A, correct_responses_A, accuracy_A)

        # calculate algorithm B accuracy
        responses_B = MLRequest.objects.filter(
            parent_mlalgorithm=ab_test.algorithm_B, 
            created_at__gt=ab_test.created_at, 
            created_at__lt=date_now
        ).count()
        correct_responses_B = MLRequest.objects.filter(
            parent_mlalgorithm=ab_test.algorithm_B, 
            created_at__gt=ab_test.created_at, 
            created_at__lt=date_now, 
            prediction=F('feedback')
        ).count()
        accuracy_B = correct_responses_B / float(responses_B)
        print(responses_B, correct_responses_B, accuracy_B)

        # select algorithm with higher accuracy
        top_algorithm, other_algorithm = ab_test.algorithm_A, ab_test.algorithm_B
        if accuracy_A < accuracy_B:
            top_algorithm, other_algorithm = other_algorithm, top_algorithm

        # assign the top algorithm to "production" status
        production_status = MLAlgorithmStatus(
            status="production",
            created_by=ab_test.created_by,
            parent_mlalgorithm=top_algorithm,
            active=True
        )
        production_status.save()
        deactivate_other_statuses(production_status)

        # assign the other algorithm to "testing" status
        testing_status = MLAlgorithmStatus(
            status="testing",
            created_by=ab_test.created_by,
            parent_mlalgorithm=other_algorithm,
            active=True
        )
        testing_status.save()
        deactivate_other_statuses(testing_status)

        summary = f"Algorithm A accuracy: {accuracy_A}, Algorithm B accuracy: {accuracy_B}"
        ab_test.ended_at = date_now
        ab_test.summary = summary
        ab_test.save()

        # except Exception as e:
        #     return Response({
        #         "status": "Error",
        #         "message": str(e),
        #         status=status.HTTP_400_BAD_REQUEST
        #     })
        return Response({
            "message": "A/B Test completed.",
            "summary": summary
        })
