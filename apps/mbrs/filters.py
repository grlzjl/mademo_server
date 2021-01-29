from django_filters import rest_framework as filters
from apps.mbrs.models import MBR

class MBRsFilter(filters.FilterSet):
    """
    报告过滤器
    """
    errorType = filters.NumberFilter(field_name='errorType')
    startDate = filters.DateTimeFilter(field_name='generationTime', lookup_expr='gte')
    endDate = filters.DateTimeFilter(field_name='generationTime', lookup_expr='lte')

    class Meta:
        model = MBR
        fields = (
            'errorType',
            'startDate',
            'endDate',
        )
