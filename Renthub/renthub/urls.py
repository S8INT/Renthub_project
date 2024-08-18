from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import PropertyListView, PropertyDetailView, PropertyCreateView

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('about/', views.about, name='about'),
    path('', views.home, name='home'),
    path('properties/', PropertyListView.as_view(), name='property_list'),
    path('property/<int:pk>/', PropertyDetailView.as_view(), name='property_detail'),
    path('property/delete/<int:pk>/', views.PropertyDeleteView, name='delete_property'),
    path('inbox/', views.inbox, name='inbox'),
    path('message/<int:receiver_id>/', views.send_message, name='send_message'),

    path('accounts/profile/', views.profile, name='profile'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/edit-profile/', views.edit_profile, name='edit_profile'),

    path('property/create/', PropertyCreateView.as_view(), name='property_create'),
    path('dashboard/add-property/', views.add_property, name='add_property'),
    path('dashboard/edit-property/<int:pk>/', views.edit_property, name='edit_property'),
    path('my-properties/', views.my_properties, name='my_properties'),
]
