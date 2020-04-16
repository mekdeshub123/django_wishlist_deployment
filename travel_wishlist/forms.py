#The use of forms.py is to place and describe all form codes for 
# easy maintainability. 
from django import forms
from django.forms import FileInput, DateInput
from .models import Place

class NewPlaceForm(forms.ModelForm):
    class Meta: #Tell django which model should be used to create "model = place".
        model = Place 
        fields = ('name', 'visited')

# a custom date inpu field created
class DateInput(forms.DateInput):
    input_type = 'date' #Overrides the default input type

class TripReviewForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ('notes', 'date_visited', 'photo')
        widgets = {
            'date_visited': DateInput()
        }
