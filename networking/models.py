import uuid

from django.db import models


class Session(models.Model):
    key = models.UUIDField(default=uuid.uuid4)


class Device(models.Model):
    name = models.CharField(max_length=256, null=False, blank=True)
    session = models.ForeignKey(Session)
    ip = models.GenericIPAddressField(blank=False, null=False, unique=True)



class Test(models.Model):
    name = models.CharField(max_length=128, unique=True)
    def __unicode__(self):
        return self.name


#class fields for Trace History will have foreign key: Source and Destination

class TraceHistory(models.Model):
    SourceIP = models.ForeignKey(Session)
    DestinationIP = models.ForeignKey(Device)
