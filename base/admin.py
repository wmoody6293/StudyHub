from django.contrib import admin

# Register your models here.
from .models import Room, Topic, Message, User

#adds Room to the admin url
admin.site.register(User)
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)