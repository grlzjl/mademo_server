"""mademo_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

from apps.mbrs.views import MBRViewSet
from apps.users.views import UsersViewSet
from apps.utils.views import UtilViewSet
from apps.summaries.views import SummariesViewSet


router = routers.DefaultRouter()
# 若存在自定义get_queryset方法的视图集，则该视图集在注册时需设置base_name
router.register(r'mbrs', MBRViewSet, base_name='mbrs')
router.register(r'summaries', SummariesViewSet, base_name='summaries')
router.register(r'users', UsersViewSet)
router.register(r'utils', UtilViewSet, base_name='utils')


schema_view = get_swagger_view(title="MA API")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('docs/', schema_view),
]
