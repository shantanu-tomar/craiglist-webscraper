from django.db import models

# Create your models here.


class Search(models.Model):
    search = models.CharField(max_length = 500)
    created = models.DateTimeField(auto_now = True)
    
    def __str__(self):
        return '{}'.format(self.search)
        
    class Meta:
        verbose_name_plural = 'Searches'


class VisitedPost(models.Model):
	post_url = models.CharField(max_length = 2048)
	post_id = models.CharField(max_length = 30, default='N/A')
	visited_on = models.DateTimeField(auto_now= True)

	def __str__(self):
		return '{}'.format(self.post_id)