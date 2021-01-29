from rest_framework import serializers
from apps.mbrs.models import MBR, ErrorType
from apps.mbrs.fields import EnumField


class MBRSerializer(serializers.ModelSerializer):
    errorType = EnumField(enum=ErrorType)
    class Meta:
        model = MBR
        fields = ('id', 'reportId', 'generationTime', 'suspectId', 'reporterId', 'longitude', 'latitude', 'errorType', 'errorCode')