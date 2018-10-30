#generic


from rest_framework import generics
from rest_framework import viewsets
from todo.models import Task
from .serializers import TodoSerializers
from django.shortcuts import redirect
from django.contrib.auth import authenticate


class TodoViewSet(viewsets.ModelViewSet):

    queryset = Task.objects.all()
    serializer_class = TodoSerializers

    def get_queryset(self):
        # Filtert den Userzugriff auf die API nach Userinhalten
       access_token = self.request.META.get('TOKEN')
       return Task.objects.filter(user = self.request.user)
