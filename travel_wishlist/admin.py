#This file is Djangos command-line utility for administrative task
#Briefly, Django addmin console used to view and manipulate data
#  in the database
from django.contrib import admin
from .models import Place

# Register your models here.

#Register the models with admin console
admin.site.register(Place)
