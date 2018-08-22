from django.urls import path

from netdisk2 import views

urlpatterns = [
    path('home/',views.login), #根目录，用户进入的首页
    # path('error/',views.error), #报错目录
    path('upload/',views.upload),
    path('logout/',views.logout),
    path('',views.home),
    path('other/file/',views.file),
    path('download/',views.download),
    path('group/add',views.group_add)
]