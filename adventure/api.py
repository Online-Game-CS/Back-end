from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# from pusher import Pusher
from django.http import JsonResponse
from decouple import config
from django.contrib.auth.models import User
from .models import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import json
from .serializers import RoomSerializer
from rest_framework import status
from random import randint

# instantiate pusher
# pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

@api_view(["GET"])
def welcome(request):
    content = {'message': 'Welcome to Lambda Mud API'}
    return JsonResponse(content)

@api_view(["GET"])
def start(request):
    # delete existing rooms
    Room.objects.all().delete()

    # create new 10 * 10 matrice
    rows = 10
    cols = 10

    grid = [None] * rows

    for i in range(0,rows):
        grid[i] = [None] * cols

    # create a room for each matrice index and save to db
    for i in range(0,rows):
        for j in range(0, cols):
            grid[i][j] = Room(i=i,j=j)
            # generate random walls
            if (randint(0,10)< 3):
                grid[i][j].wall = True
                grid[i][j].title = "Wall"
                grid[i][j].description = "Partition"
            grid[i][j].save()

    # change title of first room
    grid[0][0].title = "Starting Point"
    grid[0][0].description = "Your journey begins here"
    grid[0][0].wall = False
    grid[0][0].save()

    # create walls
    wall_positions = [(0,1), (3,0)]
    for i in wall_positions:
        grid[i[0]][i[1]].wall = True
        grid[i[0]][i[1]].title = "Wall"
        grid[i[0]][i[1]].description = "Partition"
        grid[i[0]][i[1]].save()

    # connect all rooms in matrice
    for i in range(0,rows):
        for j in range(0, cols):
            if grid[i][j].wall is False:
                grid[i][j].addConnection(grid,rows,cols)
                grid[i][j].save()

    # change rooms to bees
    bee_positions = [(0,2), (1,8), (2,3), (3,0)]
    count = 1
    for i in bee_positions:
        grid[i[0]][i[1]].wall = False
        grid[i[0]][i[1]].bee = True
        grid[i[0]][i[1]].question = count
        grid[i[0]][i[1]].title = f"Challenge {count}"
        grid[i[0]][i[1]].description = "Help Beyoncé solve this problem"
        grid[i[0]][i[1]].save()
        count += 1

    content = {'message': 'Rooms created'}
    return JsonResponse(content)

@api_view(["GET"])
def get_rooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return JsonResponse({'rooms': serializer.data}, safe=False, status=status.HTTP_200_OK) 

    
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def initialize(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    score = player.score
    room = player.room()
    players = room.playerNames(player_id)
    return JsonResponse({'uuid': uuid, 'name':player.user.username, 'room_id':room.id, 'title':room.title, 'description':room.description, 'score':score, 'players':players}, safe=True)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def complete_challenge(request):
    player = request.user.player
    player_id = player.id
    room = player.room()
    score = player.updateScore()
    print("score", score, player.score)
    players = room.playerNames(player_id)
    return JsonResponse({'name':player.user.username, 'room_id':room.id, 'title':room.title, 'score':score, 'players':players}, safe=True)

# @csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def move(request):
    dirs={"n": "north", "s": "south", "e": "east", "w": "west"}
    reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
    player = request.user.player
    player_id = player.id
    player_uuid = player.uuid
    data = json.loads(request.body)
    direction = data['direction']
    room = player.room()
    nextRoomID = None
    if direction == "n":
        nextRoomID = room.n_to
    elif direction == "s":
        nextRoomID = room.s_to
    elif direction == "e":
        nextRoomID = room.e_to
    elif direction == "w":
        nextRoomID = room.w_to
    if nextRoomID is not None and nextRoomID > 0:
        nextRoom = Room.objects.get(id=nextRoomID)
        player.currentRoom=nextRoomID
        player.save()
        players = nextRoom.playerNames(player_id)
        currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        # for p_uuid in currentPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        # for p_uuid in nextPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse({'name':player.user.username, 'room_id':nextRoom.id, 'title':nextRoom.title, 'description':nextRoom.description, 'players':players, 'error_msg':""}, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse({'name':player.user.username, 'room_id':room.id, 'title':room.title, 'description':room.description, 'players':players, 'error_msg':"You cannot move that way."}, safe=True)


@csrf_exempt
@api_view(["POST"])
def say(request):
    # IMPLEMENT
    return JsonResponse({'error':"Not yet implemented"}, safe=True, status=500)
