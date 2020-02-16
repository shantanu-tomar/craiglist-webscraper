from django.contrib import admin
from .models import Search, VisitedPost

# Register your models here.

class SearchAdmin(admin.ModelAdmin):
	list_display = ('search', 'created')


class VisitedPostAdmin(admin.ModelAdmin):
	list_display = ('post_id', 'visited_on')


admin.site.register(Search, SearchAdmin)
admin.site.register(VisitedPost, VisitedPostAdmin)