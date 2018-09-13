from django.contrib import admin
from .models import Task, Project, ChecklistItem, UserProfile, Subscriber, UserFeed, FirstFeed, UserMsg

admin.site.register(Task)
admin.site.register(Project)
admin.site.register(ChecklistItem)
admin.site.register(UserProfile)
admin.site.register(Subscriber)
admin.site.register(UserFeed)
admin.site.register(FirstFeed)
admin.site.register(UserMsg)
# Register your models here.
