import hashlib
import os
import random
import time

from django.db import models

# Create your models here.
from django.db.models.signals import post_delete
from django.dispatch import receiver

from netdisk import settings


class User(models.Model):
    user_id = models.CharField(primary_key="True", max_length=20)
    user_password = models.CharField(max_length=40, default="admin")
    user_name = models.CharField(max_length=20, default="admin")

    def __str__(self):
        return self.user_name


class Group(models.Model):
    id = models.CharField(primary_key="True", max_length=50)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=20, null=True, blank=True)
    description = models.CharField(max_length=100, default="no description")


class GrouptoUser(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class fileModel(models.Model):
    def report_path(self, filname):
        return '{}\{}'.format(self.owner_name, filname)

    def __str__(self):
        return str('%s' % self.owner_name)

    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    owner_name = models.CharField(max_length=100, null=True, blank=True)
    owner_analysis = models.SmallIntegerField(default=0)
    file = models.FileField(upload_to=report_path)
    name = models.CharField(max_length=60, null=True, blank=True, default='default')
    upload_date = models.DateTimeField(auto_now_add=True)
    file_size = models.CharField(max_length=20, null=True, blank=True)
    file_description = models.CharField(max_length=100, default="no description")


@receiver(post_delete, sender=fileModel)
def delete_upload_files(sender, instance, **kwargs):
    files = getattr(instance, 'file', '')
    if not files:
        return
    fname = os.path.join(settings.MEDIA_ROOT, str(files))
    if os.path.isfile(fname):
        os.remove(fname)
