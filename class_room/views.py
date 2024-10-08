from django.shortcuts import render
from django.conf import settings

def test_class_room(request):
    context = {
        'turn_username': settings.TURN_USERNAME,
        'turn_secret': settings.TURN_SECRET,
    }
    return render(request, 'test_class_room.html', context=context)
