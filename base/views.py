from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


#Login Page:
def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'User does not exist')

    context = {'page':page}
    return render(request, 'base/login_register.html', context)

#Logout
def logoutUser(request):
    logout(request)
    return redirect('home')

#Register
def registerPage(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password not valid')
    return render(request, 'base/login_register.html', {'form': form})
#Home Page:
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    #in our imports above, we imported Q, which allows filter chaining across multiple 
    #attributes of the model for better searching
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)         
        )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms': rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request, 'base/home.html', context)

#Room Page
def room(request, pk):
    room = Room.objects.get(id=pk)
    participants = room.participants.all()
    #below is how you query the messages for a specific room. If you look at the models.py
    #you will see that message is a child class of room, so you use the below syntax to get
    #all of the messages associated with that room
    room_messages = room.message_set.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room= room,
            body= request.POST.get('body')
        )
        #adds a participant that is new to the room when they submit a comment within the room
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room':room, 'room_messages': room_messages, 'participants':participants}
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms':rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        #form has ability to show already created topics or input new topics
        #this gets the topic name from the request object
        topic_name = request.POST.get('topic')
        #this will look into our existing Topics and look if topic_name exists already (if it does created==False)
        #if it does not already exist, created==True and new topic is added
        topic, created = Topic.objects.get_or_create(name=topic_name)

        #this is easiest way to do this given our customized form fields on room_form
        Room.objects.create(
            host = request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )

        return redirect('home')
    context = {'form': form, 'topics':topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    #check to see if logged in user is the host of a room
    #this makes sure only the host can edit/delete a room
    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        #form has ability to show already created topics or input new topics
        #this gets the topic name from the request object
        topic_name = request.POST.get('topic')
        #this will look into our existing Topics and look if topic_name exists already (if it does created==False)
        #if it does not already exist, created==True and new topic is added
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = request.POST.get('topic')
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
        
    context = {'form': form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    #check to see if logged in user is the host of a room
    #this makes sure only the host can edit/delete a room
    if request.user != room.host:
        return HttpResponse('You are not allowed here')

    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    #check to see if logged in user is the host of a room
    #this makes sure only the host can edit/delete a room
    if request.user != message.user:
        return HttpResponse('You are not allowed here')

    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        #we pass in request.FILES because we are also going to be submitting files with user creation
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    context = {'form': form}
    return render(request, 'base/update-user.html', context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context={'topics': topics}
    return render(request, 'base/topics.html', context)

def activityPage(request):
    room_messages = Message.objects.all()
    context = {'room_messages':room_messages}
    return render(request, 'base/activity.html', context)