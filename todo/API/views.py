#generic


from rest_framework import generics
from todo.models import Task
from .serializers import TodoSerializers
from django.shortcuts import redirect
from django.contrib.auth import authenticate


#class Database(generics.RetrieveUpdateDestroyAPIView): #DetailView
#    lookup_field = 'pk' # slug , id # url(r'?<pk>\d+')
#    serializer_class = TodoSerializers
#    #queryset = Task.objects.all()
#
 #   def get_queryset(self):
 #       return Task.objects.all()

    #def get_object(self):
    #   pk = self.kwargs.get("pk")
    #   return Task,objects.get(pk="pk")


#class DatabaseList(generics.ListAPIView): #DetailView

 #   lookup_field = 'pk' # slug , id # url(r'?<pk>\d+')
    #queryset = Task.objects.all()
  #  serializer_class = TodoSerializers
#
 #   def get_queryset(self):
  #      return Task.objects.all()
