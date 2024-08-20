import io

from PIL import Image
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView

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


# helper function to process image
def process_image(image):
    img = Image.open(image)
    img.thumbnail((800, 600), Image.Resampling.LANCZOS)
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=85)
    output.seek(0)
    return output


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


# Dashboard View
@login_required
def dashboard(request):
    profile = UserProfile.objects.get(user=request.user)
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
            image = form.cleaned_data.get('image')
            if image:
                output = process_image(image)
                property_instance.image.save(image.name, output, save=False)

            property_instance.save()
            return redirect('my_properties')
    else:
        form = PropertyForm()
    return render(request, 'add_property.html', {'form': form})


# Edit Property View
@login_required
def edit_property(request, pk):
    property_instance = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_instance)
        if form.is_valid():
            property_instance = form.save(commit=False)
            property_instance.owner = get_user_profile(request.user)

            image = form.cleaned_data.get('image')
            if image:
                output = process_image(image)
                property_instance.image.save(image.name, output, save=False)

            property_instance.save()
            return redirect('my_properties')
    else:
        form = PropertyForm(instance=property_instance)
    return render(request, 'edit_property.html', {'form': form})


# Delete Property View
@login_required
def property_delete(request, pk):
    property_instance = get_object_or_404(Property, pk=pk)

    if property_instance.owner.user == request.user:
        property_instance.delete()
        messages.success(request, "Property deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this property.")

    return redirect('my_properties')

# My Properties View
@login_required
def my_properties(request):
    user_profile = get_user_profile(request.user)
    properties = Property.objects.filter(owner=user_profile)
    return render(request, 'my_properties.html', {'properties': properties})


@login_required
class PropertyDeleteView(DeleteView):
    model = Property
    success_url = reverse_lazy('my_properties')
    template_name = 'property_confirm_delete.html'

    def get_queryset(self):
        owner = get_user_profile(self.request.user)
        return self.model.objects.filter(owner=owner)

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


# Add review

@login_required
def add_review(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id)
    reviewer = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.property = property_instance
            review.reviewer = reviewer
            review.save()
            return redirect('property_detail', pk=property_id)
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form, 'property': property_instance})


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
