from rest_framework.decorators import api_view
from rest_framework.response import Response

from base.models import Room

from .serializers import RoomSerializer
#If people want to download info about various pages in the application
@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ]
    return Response(routes) 

@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True) #this is for ALL the rooms, so there will be many
    print('This is the serializer: ', serializer)
    return Response(serializer.data) #all the actual data we want is stored as the value of the data key in serializer


@api_view(['GET'])
def getRoom(request, pk):
    rooms = Room.objects.get(id=pk)
    serializer = RoomSerializer(rooms, many=False) #this is for ALL the rooms, so there will be many
    return Response(serializer.data) #all the actual data we want is stored as the value of the data key in serializer
