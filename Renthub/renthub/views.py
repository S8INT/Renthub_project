from django.shortcuts import render, get_object_or_404, redirect
from .models import Property, Review, UserProfile, Message
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm, ReviewForm
# Create your views here.

def home(request):
    return render(request, 'home.html')

def property_list(request):
    query = request.GET.get('q')
    properties = Property.objects.filter(is_available=True)
    if query:
        properties = properties.filter(
            Q(title_icontains=query) |
            Q(description_icontains=query) |
            Q(address__icontains=query) |
            Q(city__icontains=query) |
            Q(property_type__icontains=query)
        )
    return render(request, 'property_list.html', {'properties': properties})

def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    reviews = property.reviews.all()
    return render(request, 'property_detail.html', {'property': property, 'reviews': reviews})

def signup (request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'profile.html', {'form': form})

@login_required
def send_message(request, receiver_id):
    sender = UserProfile.objects.get(user=request.user)
    receiver = UserProfile.objects.get(id=receiver_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        property_id = request.POST.get('property_id')
        Message.objects.create(sender=sender, receiver=receiver, content=content, property_id=property_id)
        return redirect('inbox')
    return render(request, 'send_message.html', {'receiver': receiver})

@login_required
def inbox(request):
    user_profile = UserProfile.objects.get(user=request.user)
    messages = Message.objects.filter(receiver=user_profile)
    return render(request, 'inbox.html', {'messages': messages})

@login_required
def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    reviews = property.reviews.all()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.property = property
            review.reviewer = UserProfile.objects.get(user=request.user)
            review.save()
            return redirect('property_detail', pk=pk)
    else:
        form = ReviewForm()
    return render(request, 'property_detail.html', {'property': property, 'reviews': reviews, 'form': form})