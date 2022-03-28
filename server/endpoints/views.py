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

class EndpointViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    A read-only view for a single Endpoint or a list of Endpoints.
    """
    serializer_class = EndpointSerializer
    queryset = Endpoint.objects.all()


class MLAlgorithmViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    A read-only view for a single ML algorithm or a list of ML algorithms.
    """
    serializer_class = MLAlgorithmSerializer
    queryset = MLAlgorithm.objects.all()


def deactivate_other_statuses(instance):
    old_statuses = MLAlgorithmStatus.objects.filter(parent_mlalgorithm = instance.parent_mlalgorithm,
                                                        created_at__lt=instance.created_at,
                                                        active=True)
    for status in old_statuses:
        status.active = False
    MLAlgorithmStatus.objects.bulk_update(old_statuses, ["active"])

class MLAlgorithmStatusViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet,
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
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet,
    mixins.UpdateModelMixin
):
    """
    A view for a single ML request or a list of ML requests.
    Only the feedback field may be updated due to the restrictions defined
    in the MLRequestSerializer.
    """
    serializer_class = MLRequestSerializer
    queryset = MLRequest.objects.all()