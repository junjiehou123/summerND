from django.contrib import admin

# Register your models here.

from .models import User, fileModel, Group

admin.site.register(User)
admin.site.register(fileModel)
admin.site.register(Group)