import uuid
import json

from django.db import models
from jsonfield import JSONField


class Session(models.Model):
    key = models.UUIDField(default=uuid.uuid4)


class Device(models.Model):
    name = models.CharField(max_length=256, null=False, blank=True)
    session = models.ForeignKey(Session)
    ip = models.GenericIPAddressField(blank=False, null=False, unique=True)


#class fields for Trace History will have foreign key: Source and Destination

class TraceHistory(models.Model):
    source = models.ForeignKey(Device, related_name="+")
    destination = models.ForeignKey(Device, related_name="+")
    session = models.ForeignKey(Session, related_name="history")
    hops = JSONField()

    def hopsJson(self):
        return json.loads(self.hops)
