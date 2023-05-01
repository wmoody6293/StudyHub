from django.db import models
from django.contrib.auth.models import AbstractUser

#This is where we configure the database

class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)

    avatar= models.ImageField(null=True, default="avatar.svg")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Topic(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name
    

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    #below, we set null for the db, so if we don't want to add a description it will still work
    #also below, we set blank to true so when we submit a form, it can also be blank
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    #Below, every time the save method is called it makes a timestamp
    #the auto_now creates a timestamp on every save, while the auto_now_add only 
    #creates a timestamp when it is first created
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    #order all created rooms by most recent. The dash before updated/created makes it ordered
    #with newest first, rather than ascending order
    class Meta:
        ordering = ['-updated', '-created']
    def __str__(self):
        return self.name

#message for each room
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) #if room gets deleted, all messages also get deleted
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated', '-created']
    def __str__(self):
        return self.body[0:50]