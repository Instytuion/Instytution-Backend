from django.shortcuts import render

def test_class_room(request):
    context = {}
    return render(request, 'test_class_room.html', context=context)
