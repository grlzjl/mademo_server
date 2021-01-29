from django.db import models

# 引入Enum类型
from enum import Enum
from enumfields import EnumIntegerField

class ErrorType(Enum):
    SELF = 0        # 主动上报
    CERT = 1        # 证书安全
    SEMANTIC = 2    # 消息内容

# Create your models here.
class MBR(models.Model):
    '''
    异常行为报告表
    '''

    reportId = models.CharField('报告ID', max_length=20)
    generationTime = models.DateTimeField('报告生成时间')
    suspectId = models.CharField('被举报者假名', max_length=20)
    reporterId = models.CharField('举报人假名', max_length=20)
    longitude = models.FloatField('经度')
    latitude = models.FloatField('纬度')
    errorType = EnumIntegerField(ErrorType, verbose_name='异常类型')
    errorCode = models.CharField('异常代码', max_length=2)
    createTime = models.DateTimeField('创建时间', auto_now_add=True)
    modifyTime = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        db_table = 'mbrs'