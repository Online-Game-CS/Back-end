from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import uuid

# class Room(models.Model):
#     title = models.CharField(max_length=50, default="DEFAULT TITLE")
#     description = models.CharField(max_length=500, default="DEFAULT DESCRIPTION")
#     n_to = models.IntegerField(default=0)
#     s_to = models.IntegerField(default=0)
#     e_to = models.IntegerField(default=0)
#     w_to = models.IntegerField(default=0)
#     def connectRooms(self, destinationRoom, direction):
#         destinationRoomID = destinationRoom.id
#         try:
#             destinationRoom = Room.objects.get(id=destinationRoomID)
#         except Room.DoesNotExist:
#             print("That room does not exist")
#         else:
#             if direction == "n":
#                 self.n_to = destinationRoomID
#             elif direction == "s":
#                 self.s_to = destinationRoomID
#             elif direction == "e":
#                 self.e_to = destinationRoomID
#             elif direction == "w":
#                 self.w_to = destinationRoomID
#             else:
#                 print("Invalid direction")
#                 return
#             self.save()
#     def playerNames(self, currentPlayerID):
#         return [p.user.username for p in Player.objects.filter(currentRoom=self.id) if p.id != int(currentPlayerID)]
#     def playerUUIDs(self, currentPlayerID):
#         return [p.uuid for p in Player.objects.filter(currentRoom=self.id) if p.id != int(currentPlayerID)]

class Room(models.Model):
    title = models.CharField(max_length=50, default="DEFAULT TITLE")
    description = models.CharField(max_length=500, default="DEFAULT DESCRIPTION")
    i = models.IntegerField(default=0)
    j = models.IntegerField(default=0)
    n_to = models.IntegerField(default=0)
    s_to = models.IntegerField(default=0)
    e_to = models.IntegerField(default=0)
    w_to = models.IntegerField(default=0)
    wall = models.BooleanField(default=False)

    def __str__(self):
        return f"room {self.i},{self.j}"

    def addConnection(self,grid,rows,cols):
        i = self.i
        j = self.j

        if i < rows -1 and grid[i+1][j].wall is False:
            self.s_to = grid[i+1][j].id
        if i > 0 and grid[i-1][j].wall is False:
            self.n_to = grid[i-1][j].id
        if j < cols - 1 and grid[i][j+1].wall is False:
            self.e_to = grid[i][j+1].id
        if j > 0 and grid[i][j-1].wall is False:
            self.w_to = grid[i][j-1].id
    
    def playerNames(self, currentPlayerID):
        return [p.user.username for p in Player.objects.filter(currentRoom=self.id) if p.id != int(currentPlayerID)]

    def playerUUIDs(self, currentPlayerID):
        return [p.uuid for p in Player.objects.filter(currentRoom=self.id) if p.id != int(currentPlayerID)]


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currentRoom = models.IntegerField(default=0)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    def initialize(self):
        if self.currentRoom == 0:
            self.currentRoom = Room.objects.first().id
            self.save()
    def room(self):
        try:
            return Room.objects.get(id=self.currentRoom)
        except Room.DoesNotExist:
            self.initialize()
            return self.room()

@receiver(post_save, sender=User)
def create_user_player(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)
        Token.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_player(sender, instance, **kwargs):
    instance.player.save()





