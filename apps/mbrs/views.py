from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated

from apps.mbrs.models import MBR
from apps.mbrs.serializers import MBRSerializer

# 过滤器
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from apps.mbrs.filters import MBRsFilter

import datetime


class MBRViewSet(viewsets.ModelViewSet):
    queryset = MBR.objects.all()
    serializer_class = MBRSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = MBRsFilter

    # 用于返回假名数量统计的接口
    @action(methods=['GET'], detail=False)
    def topchart(self, request):
        """
        按假名证书汇总数量
        ---
        ## request:

        |参数名|描述|请求类型|参数类型|备注|
        |:----:|:----:|:----:|:----:|:----:|
        | startDate | 起始时间 | query | string | `YYYY-MM-DD` 默认当日 |
        | top | 返回个数 | query | string | 默认全部返回 |

        ## response:
        ``` json
        {
            "suspect": [
                {
                  "name": "假名",
                  "value": 数量，
                }
            ],
            "reporter": [
                {
                  "name": "假名",
                  "value": 数量，
                }
            ]
        }
        """
        queryset = MBR.objects.all()
        date_format = '%Y-%m-%d'
        if "startDate" in self.request.query_params:
            startDate = self.request.query_params.get('time_type')
        else:
            startDate = datetime.date.today().strftime(date_format)

        suspect_stat = queryset.filter(generationTime__gte=startDate).extra(select={'name': 'suspectId'})\
            .values('name').annotate(value=Count('id')).order_by('-value')
        reporter_stat = queryset.filter(generationTime__gte=startDate).extra(select={'name': 'reporterId'})\
            .values('name').annotate(value=Count('id')).order_by('-value')

        suspect_stat = list(suspect_stat)
        reporter_stat = list(reporter_stat)

        if 'top' in self.request.query_params:
            top1 = top2 = int(self.request.query_params.get('top'))
        else:
            top1 = len(suspect_stat)
            top2 = len(reporter_stat)

        result = {
            'suspect': suspect_stat[:top1],
            'reporter': reporter_stat[:top2]
        }
        return Response(data=result, status=status.HTTP_200_OK)
