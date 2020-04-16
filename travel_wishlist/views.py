from django.shortcuts import render, redirect, get_object_or_404
from .models import Place
from .forms import NewPlaceForm, TripReviewForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

#This view will handle requests to home page

@login_required
def place_list(request):
    if request.method == 'POST':
        form = NewPlaceForm(request.POST)
        place = form.save(commit=False) #create a new place from the form
        place.user = request.user # Associate the place with the logged-in user
        if form.is_valid():#Checks against DB constraints.
            place.save()#saves to the DB
            return redirect('place_list')#Redirect to GET view with the name place_list

    #if not a POST, or the form is not valid, render the page with the 
    # form to add a new place and list of place
    places = Place.objects.filter(user=request.user).filter(visited=False).order_by('name')#it allow run query against the table and returns query set obj(s)
    new_place_form = NewPlaceForm()#form object created
    return render(request, 'travel_wishlist/wishlist.html', { 'places': places, 'new_place_form': new_place_form})

@login_required
def places_visited(request):
    #Fetched the data from the database and sorted by 
    # user visited and display it in the view
    visited = Place.objects.filter(user=request.user).filter(visited=True)
    return render(request, 'travel_wishlist/visited.html', {'visited': visited})

@login_required
def place_was_visited(request):
    if request.method == "POST":
        pk = request.POST.get("pk")#get the pk vlaue from the form
        place = get_object_or_404(Place, pk=pk)#it tests if user rquest pk that not in the database
        print(place.user, request.user)
        if place.user == request.user:
            place.visited = True#update the visited to true
            place.save()
        else:
            return HttpResponseForbidden()
    return redirect('place_list')

@login_required
def place_details(request, place_pk):
    place = get_object_or_404(Place, pk=place_pk)

    #Check if the place and user match.
    if place.user != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = TripReviewForm(request.POST, request.FILES, instance=place)
        #Instance is the model object to update with the form data
        if form.is_valid():
            form.save()
            messages.info(request, 'Trip information updated!')
        else:
            messages.error(request, form.errors)#Templet error message.
        return redirect('place_details', place_pk=place_pk)
    
    else: #get place detail
        if place.visited:
            review_form = TripReviewForm(instance=place)#pre-populate with data from this place instance
            return render(request, 'travel_wishlist/place_detail.html', {'place': place, 'review_form': review_form})
        else:
            return render(request, 'travel_wishlist/place_detail.html', {'place': place})

@login_required
def delete_place(request, place_pk):
    place = get_object_or_404(Place, pk=place_pk)
    if place.user == request.user:
        place.delete()
        return redirect('place_list')
    else:
        return HttpResponseForbidden()
