import io

from PIL import Image
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView

from .forms import CustomAuthenticationForm
from .forms import UserProfileForm, ReviewForm, PropertyForm
from .models import Property, UserProfile, Message


# create your views here


# Helper function to get UserProfile
def get_user_profile(user):
    try:
        return UserProfile.objects.get(user=user)
    except ObjectDoesNotExist:
        return None


# Homepage View
def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'About.html')


# Property List View using Class-Based Views
class PropertyListView(ListView):
    model = Property
    template_name = 'property_list.html'
    context_object_name = 'properties'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        queryset = Property.objects.filter(is_available=True)
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(property_type__icontains=query)
            )
        return queryset


# Property Detail View with Reviews
class PropertyDetailView(DetailView):
    model = Property
    template_name = 'property_detail.html'
    context_object_name = 'property'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.select_related('reviewer').all()
        context['form'] = ReviewForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.property = self.get_object()
            review.reviewer = get_user_profile(request.user)
            review.save()
            return redirect('property_detail', pk=self.get_object().pk)
        return self.get(request, *args, **kwargs)


# Signup View
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


# Logout View
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return render(request, 'registration/logout.html')


# Dashboard View
@login_required
def dashboard(request):
    profile = get_user_profile(request.user)
    properties = Property.objects.filter(owner=profile)
    return render(request, 'dashboard.html', {'profile': profile, 'properties': properties})


# Profile View
@login_required
def profile(request):
    user_profile = get_user_profile(request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'profile.html', {'form': form})

# Send Message View
@login_required
def send_message(request, receiver_id):
    sender = get_user_profile(request.user)
    receiver = get_object_or_404(UserProfile, id=receiver_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        property_id = request.POST.get('property_id')
        Message.objects.create(sender=sender, receiver=receiver, content=content, property_id=property_id)
        return redirect('inbox')
    return render(request, 'send_message.html', {'receiver': receiver})


# Inbox View
@login_required
def inbox(request):
    user_profile = get_user_profile(request.user)
    messages = Message.objects.filter(receiver=user_profile).select_related('sender', 'property')
    return render(request, 'inbox.html', {'messages': messages})

# My Properties View
@login_required
def my_properties(request):
    user_profile = get_user_profile(request.user)
    properties = Property.objects.filter(owner=user_profile)
    return render(request, 'my_properties.html', {'properties': properties})


# Property Create View
class PropertyCreateView(CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'property_form.html'
    success_url = reverse_lazy('my_properties')

    def form_valid(self, form):
        property = form.save(commit=False)
        property.owner = get_user_profile(self.request.user)
        property.save()
        return redirect(self.success_url)


# property Add View
@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_instance = form.save(commit=False)
            property_instance.owner = get_user_profile(request.user)
            # Resize and optimize image
            image = form.cleaned_data.get('image')
            if image:
                img = Image.open(image)
                img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85)
                output.seek(0)
                property_instance.save(image.name, output, save=False, content_type='image/jpeg', charset=None)

            property_instance.save()
            return redirect('my_properties')
    else:
        form = PropertyForm()
    return render(request, 'add_property.html', {'form': form})


# Property Edit View
@login_required
def edit_property(request, pk):
    property_instance = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_instance)
        if form.is_valid():
            property_instance = form.save(commit=False)
            property_instance.owner = get_user_profile(request.user)

            # Resize and optimize image if a new one is provided
            image = form.cleaned_data.get('image')
            if image:
                img = Image.open(image)
                img = img.resize((800, 600), Image.Resampling.LANCZOS)
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85)
                output.seek(0)
                property_instance.image.save(image.name, output, save=False)

            property_instance.save()
            return redirect('my_properties')
    else:
        form = PropertyForm(instance=property_instance)
    return render(request, 'edit_property.html', {'form': form})
@login_required
def my_properties(request):
    user_profile = get_user_profile(request.user)
    properties = Property.objects.filter(owner=user_profile)
    return render(request, 'my_properties.html', {'properties': properties})


@login_required
def property_delete(request, pk):
    property = get_object_or_404(Property, pk=pk)
    if property.owner and property.owner.user == request.user:
        property.delete()
    return redirect('my_properties')


# Edit Profile View
@login_required
def edit_profile(request):
    profile = get_user_profile(request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})


# Login View
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})
