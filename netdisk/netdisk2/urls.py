from django.urls import path

from netdisk2 import views

urlpatterns = [
    path('home/',views.login), #根目录，用户进入的首页
    # path('error/',views.error), #报错目录
    path('upload/',views.upload),
    path('register/',views.register),
    path('logout/',views.logout),
    path('',views.home),
    path('other/file/',views.file),
    path('download/',views.download),
    path('group/create',views.group_create),
    path('group/my',views.group_my),
    path('group/add',views.group_add),
    path('group/detail',views.group_detail),
    path('group/delete',views.group_delete),
    path('other/delete',views.delete)
]