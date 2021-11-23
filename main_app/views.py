from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Trip, Photo
from datetime import date
import uuid
import boto3

S3_BASE_URL = 'https://s3-us-west-1.amazonaws.com/'
BUCKET = 'catcollector-photo-uploadan'


# Create your views here.
from django.http import HttpResponse

# Define the home view
def home(request):
  return render(request, 'home.html')

def about(request):
  return render(request, 'about.html')

@login_required
def upcomingtrips_index(request):
  today = date.today()
  trips = Trip.objects.filter(user=request.user).filter(date__gte=today)
  return render(request, 'trips/index.html', { 'trips': trips })


@login_required
def pasttrips_index(request):
  today = date.today()
  trips = Trip.objects.filter(user=request.user).filter(date__lte=today)
  return render(request, 'trips/indexpast.html', { 'trips': trips })

@login_required
def trips_detail(request, trip_id):
  trip = Trip.objects.get(id=trip_id)
  return render(request, 'trips/detail.html', { 'trip': trip })

@login_required
def pasttrips_detail(request, trip_id):
  trip = Trip.objects.get(id=trip_id)
  return render(request, 'trips/pastdetail.html', { 'trip': trip })

def add_photo(request, trip_id):
    # photo-file will be the "name" attribute on the <input type="file">
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        # need a unique "key" for S3 / needs image file extension too
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # just in case something goes wrong
        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            # build the full url string
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            # we can assign to cat_id or cat (if you have a cat object)
            photo = Photo(url=url, trip_id=trip_id)
            photo.save()
        except:
            print('An error occurred uploading file to S3')
    return redirect('detail', trip_id=trip_id)


class TripCreate(LoginRequiredMixin, CreateView):
  model = Trip
  fields = ['trip_organizer', 'attending', 'location', 'budget', 'date', 'plan', 'notes']
  def form_valid(self, form):
    # Assign the logged in user (self.request.user)
    form.instance.user = self.request.user  # form.instance is the cat
    # Let the CreateView do its job as usual
    return super().form_valid(form)

def signup(request):
  error_message = ''
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # This will add the user to the database
      user = form.save()
      # This is how we log a user in via code
      login(request, user)
      return redirect('index')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)

class TripUpdate(LoginRequiredMixin, UpdateView):
  model = Trip
  fields = ['trip_organizer', 'attending', 'location', 'budget', 'date', 'plan', 'notes']

class TripDelete(LoginRequiredMixin, DeleteView):
  model = Trip
  success_url = '/upcomingtrips/'

# class Trip:  # Note that parens are optional if not inheriting from another class
#   def __init__(self, First_name, Last_name, vaccinated, location, date, Past_trip, images, review):
#     self.First_name = First_name
#     self.Last_name = Last_name
#     self.vaccinated = vaccinated
#     self.location = location
#     self.date = date
#     self.Past_trip = Past_trip
#     self.images = images
#     self.review = review

# trips = [
#   Trip('Dan', 'Werm', True, 'Germany', 'Nov-12-2022', False, None, None),
# #   Trip('Sachi', 'tortoise shell', 'diluted tortoise shell', 0),
# #   Trip('Raven', 'black tripod', '3 legged cat', 4)
# ]
