from django.shortcuts import render


def index(request):
    return render(request, 'game_engine/index.html')

def room(request, user_name, room_name):
    return render(request, 'game_engine/room.html', {
        'room_name': room_name,
        'user_name': user_name
    })