import hashlib
import json
import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.http import FileResponse

# Create your views here.
from django.utils.encoding import escape_uri_path
from django.views.decorators.csrf import csrf_exempt

from netdisk2 import models
from netdisk2.models import fileModel, User, Group, GrouptoUser


def home(request):
    if request.session.get('is_login') is None:
        return render(request, 'login.html')
    return redirect("./home")


def upload(request):
    if request.session.get('is_login') is None:
        return render(request, 'login.html')
    status = "failure"
    if request.method == 'GET':
        return render(request, "upload.html")
    if request.method == 'POST':
        user = User.objects.get(user_id=request.session.get("user"))
        group = Group.objects.filter(id=request.POST.get("group"))
        try:
            data = request.FILES['fafafa']
        except:
            message = "上传文件不能为空"
            if group:
                return render(request, 'group_detail.html', {"message": message})
            else:
                return render(request, 'upload.html', {"message": message})
        if data:
            file = fileModel.objects.get(name=data.name, owner=user)
            # 名字如果相同，返回提示message
            # 判断是个人文件还是群组文件
            if group:
                if file:
                    message = "您已上传过同名文件，请更改文件名"
                    return render(request, 'group_detail.html', {"message": message})
                else:
                    message = "上传成功"
                    temp_file = fileModel(file=data, owner_name=group.id, owner=user, owner_analysis=1, group=group,
                                          name=data.name)
                    temp_file.save()
                    return render(request, 'group_detail.html', {"message": message})
            else:
                owner_name = user.user_id
                if file:
                    message = "您已上传过同名文件，请更改文件名"
                    return render(request, 'upload.html', {"message": message})
                else:
                    message = "上传成功"
                    temp_file = fileModel(file=data, owner_name=owner_name, owner=user, owner_analysis=0,
                                          name=data.name)
                    temp_file.save()
                    return render(request, 'upload.html', {"message": message})


def login(request):
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
    downloadfile = "netdisk2/myCloud/templates/static/upload/" + file_name
    fil = open(downloadfile, 'rb')
    response = FileResponse(fil)
    response['Content-Type'] = 'application/octet-stream'
    file_name = file_name[file_name.find("/") + 1:]
    response['Content-Disposition'] = "attachment;filename*=utf-8''{}".format(escape_uri_path(file_name))
    return response


@csrf_exempt
def group_create(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/netdisk2/home")
    if request.method == 'GET':
        return render(request, "group_create.html")
    if request.method == 'POST':
        group_name = str(request.POST.get("name"))
        group_description = str(request.POST.get("description"))
        user = User.objects.get(user_id=request.session.get("user"))
        md5 = hashlib.md5(str(group_name + group_description + str(user)).encode('utf - 8')).hexdigest()
        exist = Group.objects.filter(id=md5)
        if exist:
            return JsonResponse(json.dumps({
                "status": -1}), safe=False)
        group = models.Group(group_name=group_name, description=group_description, creator=user, id=md5)
        group.save()
        grouptouser = models.GrouptoUser(group=group, user=user)
        grouptouser.save()
        return JsonResponse(json.dumps({
            "status": 1,
            "code": md5}), safe=False)


def group_my(request):
    l = dict()
    p = list()
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/netdisk2/home")
    if request.method == 'GET':
        user = request.session.get("user")
        group = GrouptoUser.objects.filter(user=user)
        for detail in group:
            p.append(detail.group)
        return render(request, "group_my.html", {"group": p})
    return redirect("/netdisk2/home")


@csrf_exempt
def group_add(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/netdisk2/home")
    if request.method == 'GET':
        return render(request, "group_add.html")
    if request.method == 'POST':
        code = request.POST.get("code")
        user = models.User.objects.get(user_id=request.session.get("user"))
        group = models.Group.objects.filter(id=code)
        if group:
            status = models.GrouptoUser.objects.get(user=user, group=group[0])
            # status 如果找得到说明已经加入了返回1,未添加返回0，未找到该邀请码返回2
            if status:
                message = "已经加入，无需重复添加"
                print(message)
                return render(request, "group_add.html", {"message": message})
            else:
                grouptouser = models.GrouptoUser(group=group, user=user)
                grouptouser.save()
                message = "添加成功"
                print(message)
                return render(request, "group_add.html", {"message": message})
        else:
            message = "未找到该邀请码对应的群组"
            return render(request, "group_add.html", {"message": message})


def group_detail(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/netdisk2/home")
    if request.method == "GET":
        user = User.objects.get(user_id=request.session.get("user"))
        group_id = request.GET.get("id")
        group = models.Group.objects.get(id=group_id)
        status = GrouptoUser.objects.get(user=user, group=group)
        file_list = models.fileModel.objects.filter(group=group, owner_analysis=1)
        if status:
            return render(request, 'group_detail.html', {"file_list": file_list, "group": group})
        else:
            return render(request, 'group_my.html')
    else:
        user = request.session.get('user')
        file_list = models.fileModel.objects.filter(owner=user)
    return render(request, 'file.html', {"file_list": file_list})


def register(request):
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
                user = models.User.objects.get(user_id=username)
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
