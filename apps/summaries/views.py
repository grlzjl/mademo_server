from rest_framework.decorators import action
from rest_framework.schemas import AutoSchema
from rest_framework.response import Response
from rest_framework import viewsets, status
from coreapi import Field, Link, document
import coreschema

from django.db.models import Count

from apps.summaries.serializers import SummariesSerializer
from apps.mbrs.models import MBR
from datetime import datetime


# 折线图处理，目的是将没有数据的月份补零
def lineChart_handle(time_type, stats):
    time_list = list(set([item['time'] for stat in stats for item in stat]))
    if not time_list:
        return []
    max_time = max(time_list)
    time_format = '%Y-%m' if time_type == 'YEAR' else '%Y-%m-%d'
    dt = datetime.strptime(max_time, time_format)
    upper_limit = dt.month if time_type == 'YEAR' else dt.day
    def init_time(time):
        day = 1 if time_type == 'YEAR' else time
        month = time if time_type == 'YEAR' else dt.month
        year = dt.year
        return datetime(day=day, month=month, year=year).strftime(time_format)

    full_time = list(map(init_time, range(1, upper_limit + 1)))
    init_data = [[0] * upper_limit for _ in range(len(stats))]
    for i in range(upper_limit):
        for j, item_list in enumerate(stats):
            for item in item_list:
                if item['time'] == full_time[i]:
                    init_data[j][i] = item['count']
                    break
    return {
        'time': full_time,
        'self': init_data[0],
        'cert': init_data[1],
        'semantic': init_data[2]
    }


def lineChart_handle2(time_type, time_stat):
    time_list = [item['time'] for item in time_stat]
    if not time_list:
        return []
    max_time = max(time_list)
    time_format = '%Y-%m' if time_type == 'YEAR' else '%Y-%m-%d'
    dt = datetime.strptime(max_time, time_format)
    upper_limit = dt.month if time_type == 'YEAR' else dt.day
    def init_item(item):
        day = 1 if time_type == 'YEAR' else item
        month = item if time_type == 'YEAR' else dt.month
        year = dt.year
        return {
            'time': datetime(day=day, month=month, year=year).strftime(time_format),
            'count': 0
        }

    init_data = map(init_item, range(1, upper_limit + 1))
    init_data = list(init_data)
    # merge init_data & time_stat
    for init_item in list(init_data):
        for stat_item in time_stat:
            if init_item['time'] == stat_item['time']:
                init_item['count'] = stat_item['count']
                break
    return init_data


# 柱状图处理，目的是将没有数据的类别补零
def barChart_handle(errorType, stat_data):
    init_data = barChart_handle2(errorType, stat_data)
    codes = []
    counts = []
    init_data.sort(key=lambda x: int(x['errorCode']))
    for item in init_data:
        codes.append(item['errorCode'])
        counts.append(item['count'])
    return {
        'erorrCode': codes,
        'count': counts
    }


def barChart_handle2(errorType, stat_data):
    codeRange = [8, 11, 9]  # 子类别数量
    init_data = [{'errorCode': str(i).zfill(2), 'count': 0} for i in range(codeRange[errorType])]
    for init_item in init_data:
        for stat_item in stat_data:
            if init_item['errorCode'] == stat_item['errorCode']:
                init_item['count'] = stat_item['count']
                break
    return init_data


class CustomAutoSchema(AutoSchema):
    def get_link(self, path, method, base_url):
        link = super().get_link(path, method, base_url)
        fields = [
            Field(
                'time_type',
                location='query',
                required=True,
                schema=coreschema.Enum(enum=['year', 'month'])),
            Field(
                'time_value',
                location='query',
                required=True,
                schema=coreschema.String()),
        ]
        fields = tuple(fields)
        link = Link(
            url=link.url,
            action=link.action,
            encoding=link.encoding,
            fields=fields,
            description=link.description)
        document.Link()
        return link


class SummariesViewSet(viewsets.GenericViewSet):
    schema = CustomAutoSchema()

    def get_queryset(self):
        serializer = SummariesSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        time_type = self.request.query_params.get('time_type')
        time_value = self.request.query_params.get('time_value')
        if time_type == 'YEAR':
            return MBR.objects.filter(
                generationTime__year=time_value)
        if time_type == 'MONTH':
            time_value = time_value.split('-', 1)
            return MBR.objects.filter(
                generationTime__year=time_value[0],
                generationTime__month=time_value[1])

    @action(methods=['GET'], detail=False)
    def piechart(self, request):
        """
        饼图

        ---

        ## request:

        |参数名|描述|请求类型|参数类型|备注|
        |:----:|:----:|:----:|:----:|:----:|
        | time_type | 时间类型 | query | string | `YEAR` or `MONTH` |
        | time_value | 时间值 | query | string |  `YYYY` or `YYYY-MM`|

        ## response:
        ``` json
        {
            "time": "统计时间",
            "total_count": "异常报告数量"，
            "self_count": "主动上报异常数量",
            "cert_count": "证书安全异常数量",
            "semantic_count": "消息内容异常数量",
        }
        """
        query = self.get_queryset()

        result = query.values('errorType').annotate(
            counts=Count('id')).order_by()

        try:
            self_count = result.get(errorType=0)['counts']
        except MBR.DoesNotExist:
            self_count = 0
        try:
            cert_count = result.get(errorType=1)['counts']
        except MBR.DoesNotExist:
            cert_count = 0
        try:
            semantic_count = result.get(errorType=2)['counts']
        except MBR.DoesNotExist:
            semantic_count = 0

        res_dict = {
            'time': request.query_params.get('time_value'),
            'self_count': self_count,
            'cert_count': cert_count,
            'semantic_count': semantic_count,
            'total_count': self_count + cert_count + semantic_count
        }
        return Response(data=res_dict, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def linechart(self, request):
        """
        折线图

        ---

        ## request:

        |参数名|描述|请求类型|参数类型|备注|
        |:----:|:----:|:----:|:----:|:----:|
        | time_type | 时间类型 | query | string | `YEAR` or `MONTH` |
        | time_value | 时间值 | query | string |  `YYYY` or `YYYY-MM`|

        ## response:
        ``` json
        {
            "time": ["YYYY-MM or YYYY-MM-DD"],
            "self": ["数量"],
            "cert": ["数量"],
            "semantic": ["数量"]
        }
        """
        time_type = self.request.query_params.get('time_type')
        queryset = self.get_queryset()

        if time_type == 'YEAR':
            stat_self = queryset.filter(errorType=0).extra({
                'time': 'DATE_FORMAT(generationTime, "%%Y-%%m")'
            }).values('time').annotate(count=Count('id')).order_by()
            stat_cert = queryset.filter(errorType=1).extra({
                'time': 'DATE_FORMAT(generationTime, "%%Y-%%m")'
            }).values('time').annotate(count=Count('id')).order_by()
            stat_semantic = queryset.filter(errorType=2).extra({
                'time': 'DATE_FORMAT(generationTime, "%%Y-%%m")'
            }).values('time').annotate(count=Count('id')).order_by()

        if time_type == 'MONTH':
            stat_self = queryset.filter(errorType=0).extra({
                'time': 'DATE_FORMAT(generationTime, "%%Y-%%m-%%d")'
            }).values('time').annotate(count=Count('id')).order_by()
            stat_cert = queryset.filter(errorType=1).extra({
                'time': 'DATE_FORMAT(generationTime, "%%Y-%%m-%%d")'
            }).values('time').annotate(count=Count('id')).order_by()
            stat_semantic = queryset.filter(errorType=2).extra({
                'time': 'DATE_FORMAT(generationTime, "%%Y-%%m-%%d")'
            }).values('time').annotate(count=Count('id')).order_by()

        stat_self = list(stat_self)
        stat_cert = list(stat_cert)
        stat_semantic = list(stat_semantic)

        data = lineChart_handle(time_type, [stat_self, stat_cert, stat_semantic])

        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def linechart2(self, request):
        """
        折线图2

        ---

        ## request:

        |参数名|描述|请求类型|参数类型|备注|
        |:----:|:----:|:----:|:----:|:----:|
        | time_type | 时间类型 | query | string | `YEAR` or `MONTH` |
        | time_value | 时间值 | query | string |  `YYYY` or `YYYY-MM`|

        ## response:
        ``` json
        {
            "self": [
                {
                    "time": "YYYY-MM or YYYY-MM-DD",
                    "count": "数量"
                }
            ],
            "cert": [
                {
                    "time": "YYYY-MM or YYYY-MM-DD",
                    "count": "数量"
                }
            ],
            "semantic": [
                {
                    "time": "YYYY-MM or YYYY-MM-DD",
                    "count": "数量"
                }
            ]
        }
        """
        time_type = self.request.query_params.get('time_type')
        queryset = self.get_queryset()

        if time_type == 'YEAR':
            stat_self = queryset.filter(errorType=0).extra({
                'time': 'DATE_FORMAT(generationTime, "%%Y-%%m")'
            }).values('time').annotate(count=Count('id')).order_by()
            stat_cert = queryset.filter(errorType=1).extra({
                'time': 'DATE_FORMAT(generationTime, "%%Y-%%m")'
            }).values('time').annotate(count=Count('id')).order_by()
            stat_semantic = queryset.filter(errorType=2).extra({
                'time': 'DATE_FORMAT(generationTime, "%%Y-%%m")'
            }).values('time').annotate(count=Count('id')).order_by()

        if time_type == 'MONTH':
            stat_self = queryset.filter(errorType=0).extra({
                'time': 'DATE_FORMAT(generationTime, "%%Y-%%m-%%d")'
            }).values('time').annotate(count=Count('id')).order_by()
            stat_cert = queryset.filter(errorType=1).extra({
                'time': 'DATE_FORMAT(generationTime, "%%Y-%%m-%%d")'
            }).values('time').annotate(count=Count('id')).order_by()
            stat_semantic = queryset.filter(errorType=2).extra({
                'time': 'DATE_FORMAT(generationTime, "%%Y-%%m-%%d")'
            }).values('time').annotate(count=Count('id')).order_by()

        stat_self = list(stat_self)
        stat_cert = list(stat_cert)
        stat_semantic = list(stat_semantic)

        self_data = lineChart_handle2(time_type, stat_self)
        cert_data = lineChart_handle2(time_type, stat_cert)
        semantic_data = lineChart_handle2(time_type, stat_semantic)

        result = {
            'self': self_data,
            'cert': cert_data,
            'semantic': semantic_data
        }
        return Response(data=result, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def barchart(self, request):
        """
        柱状图

        ---

        ## request:

        |参数名|描述|请求类型|参数类型|备注|
        |:----:|:----:|:----:|:----:|:----:|
        | time_type | 时间类型 | query | string | `YEAR` or `MONTH` |
        | time_value | 时间值 | query | string |  `YYYY` or `YYYY-MM`|

        ## response:
        ``` json
        {
            "self": {
                    "errorCode": ["代码",]
                    "count": ["数量"]
            },
            "cert": {
                    "errorCode": ["代码",]
                    "count": ["数量"]
            },
            "semantic": {
                    "errorCode": ["代码",]
                    "count": ["数量"]
            }
        }
        """
        queryset = self.get_queryset()

        self_stat = queryset.filter(errorType=0).values('errorCode').annotate(
            count=Count('id')).order_by()
        cert_stat = queryset.filter(errorType=1).values('errorCode').annotate(
            count=Count('id')).order_by()
        semantic_stat = queryset.filter(errorType=2).values('errorCode').annotate(
            count=Count('id')).order_by()

        self_stat = list(self_stat)
        cert_stat = list(cert_stat)
        semantic_stat = list(semantic_stat)

        if self_stat:
            self_stat = barChart_handle(0, self_stat)
        if cert_stat:
            cert_stat = barChart_handle(1, cert_stat)
        if semantic_stat:
            semantic_stat = barChart_handle(2, semantic_stat)

        result = {
            'self': self_stat,
            'cert': cert_stat,
            'semantic': semantic_stat
        }
        return Response(data=result, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def barchart2(self, request):
        """
        柱状图2

        ---

        ## request:

        |参数名|描述|请求类型|参数类型|备注|
        |:----:|:----:|:----:|:----:|:----:|
        | time_type | 时间类型 | query | string | `YEAR` or `MONTH` |
        | time_value | 时间值 | query | string |  `YYYY` or `YYYY-MM`|

        ## response:
        ``` json
        {
            "self": [
                {
                    "errorCode": "代码",
                    "count": "数量"
                }
            ],
            "cert": [
                {
                    "errorCode": "代码",
                    "count": "数量"
                }
            ],
            "semantic": [
                {
                    "errorCode": "代码",
                    "count": "数量"
                }
            ]
        }
        """
        queryset = self.get_queryset()

        self_stat = queryset.filter(errorType=0).values('errorCode').annotate(
            count=Count('id')).order_by()
        cert_stat = queryset.filter(errorType=1).values('errorCode').annotate(
            count=Count('id')).order_by()
        semantic_stat = queryset.filter(errorType=2).values('errorCode').annotate(
            count=Count('id')).order_by()

        self_stat = list(self_stat)
        cert_stat = list(cert_stat)
        semantic_stat = list(semantic_stat)

        if self_stat:
            self_stat = barChart_handle2(0, self_stat)
        if cert_stat:
            cert_stat = barChart_handle2(1, cert_stat)
        if semantic_stat:
            semantic_stat = barChart_handle2(2, semantic_stat)

        result = {
            'self': self_stat,
            'cert': cert_stat,
            'semantic': semantic_stat
        }
        return Response(data=result, status=status.HTTP_200_OK)