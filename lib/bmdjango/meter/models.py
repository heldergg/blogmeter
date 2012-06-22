from django.db import models
from datetime import datetime

class Blog( models.Model ):

    name = models.CharField(max_length=64)
    url = models.URLField()
    sitemeter_key = models.CharField(max_length=64, unique=True)

class Stats( models.Model ):
    blog = models.ForeignKey('Blog')
    
    timestamp = models.DateTimeField(default=datetime.now)

    visits_total = models.IntegerField()
    visits_daily_average = models.IntegerField()
    visits_lenght_average = models.IntegerField()
    visits_last_hour = models.IntegerField()
    visits_today = models.IntegerField()
    visits_this_week = models.IntegerField()
    pages_total = models.IntegerField()
    pages_daily_average = models.IntegerField()
    pages_lenght_average = models.IntegerField()
    pages_last_hour = models.IntegerField()
    pages_today = models.IntegerField()
    pages_this_week = models.IntegerField()
