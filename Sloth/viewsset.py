
from django.shortcuts import redirect


def goto(request):
    return redirect('todo:login')
