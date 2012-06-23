from django.db import models
from datetime import date

class Blog( models.Model ):

    name = models.CharField(max_length=64)
    url = models.URLField()
    sitemeter_key = models.CharField(max_length=64, unique=True)

    error_count = models.IntegerField(default=0)

    def sitemeter_url(self):
        return 'http://www.sitemeter.com/default.asp?action=stats&site=%s' % self.sitemeter_key

##
# Stats
##

class Stats( models.Model ):
    blog = models.ForeignKey('Blog')
    
    date = models.DateField(default=date.today)

    visits_total = models.IntegerField()
    visits_daily_average = models.IntegerField()
    visits_lenght_average = models.IntegerField()
    visits_last_hour = models.IntegerField()
    visits_today = models.IntegerField()
    visits_this_week = models.IntegerField()
    pages_total = models.IntegerField()
    pages_daily_average = models.IntegerField()
    pages_visit_average = models.FloatField()
    pages_last_hour = models.IntegerField()
    pages_today = models.IntegerField()
    pages_this_week = models.IntegerField()

    class Meta:
        unique_together = (('blog','date'),)
