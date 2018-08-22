import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.http import FileResponse

# Create your views here.
from django.utils.datetime_safe import time

from netdisk2 import models
from netdisk2.models import fileModel, User


def home(request):
    return redirect("./home")


def upload(request):
    if request.session.get('is_login') is None:
        return render(request, 'login.html')
    status = "failure"
    if request.method == 'GET':
        return render(request, "upload.html")
    if request.method == 'POST':
        data = request.FILES['fafafa']
        # 找到userid
        user = User.objects.get(user_id=request.session.get("user"))
        owner_name = user.user_name
        temp_file = fileModel(file=data, owner_name=owner_name, owner=user)
        temp_file.save()
        status = "success"
        # 这里可以改成继续传递的形式，不返回一个jsonresponse，而是一个路径
    return JsonResponse(status, safe=False)


def login(request):
    is_login = request.session.get('is_login')
    if request.session.get('is_login') is True:
        return render(request, 'home.html')
    if request.method == "POST":
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        message = "所有字段都必须填写！"
        if username and password:  # 确保用户名和密码都不为空
            username = username.strip()
            # 用户名字符合法性验证
            # 密码长度验证
            # 更多的其它验证.....
            try:
                user = models.User.objects.get(user_name=username)
                if user.user_password == password:
                    request.session['is_login'] = True
                    request.session['user'] = user.user_id
                    return redirect('/netdisk2/home')
                else:
                    message = "密码不正确！"
            except:
                message = "用户名不存在！"
        return render(request, 'login.html', {"message": message})
    return render(request, 'login.html')


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/netdisk2/home")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/netdisk2/home")


def file(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/netdisk2/home")
    if request.method == "POST":
        return render(request, 'login.html')
    else:
        user = request.session.get('user')
        file_list = models.fileModel.objects.filter(owner=user)
    return render(request, 'file.html', {"file_list": file_list})


def download(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/netdisk2/home")
    id = request.GET.get("downloadfile")
    file = fileModel.objects.get(id=id)
    file_name = str(file.file)
    print("下载文件" + file_name)
    downloadfile = "netdisk2/myCloud/templates/static/upload/" + file_name
    fil = open(downloadfile, 'rb')
    response = FileResponse(fil)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename=' + file_name
    return response


def group_add(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/netdisk2/home")
    if request.method == 'GET':
        return render(request, "group.html")
