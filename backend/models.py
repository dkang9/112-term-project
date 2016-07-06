from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

class Form(models.Model):
    name = models.CharField(max_length=30)
    region = models.CharField(max_length=4)
    lane = models.CharField(max_length=10)
    partner =  models.CharField(max_length=20)
    pref = models.CharField(max_length=200)
    rank = models.CharField(max_length=10)
    mostPlayed = models.CharField(max_length=200)
    winRate = models.CharField(max_length=200)
    kda = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
