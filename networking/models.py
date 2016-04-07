import uuid

from django.db import models


class Session(models.Model):
    key = models.UUIDField(default=uuid.uuid4)


class Device(models.Model):
    name = models.CharField(max_length=256, null=False, blank=True)
    session = models.ForeignKey(Session)
    ip = models.GenericIPAddressField(blank=False, null=False, unique=True)