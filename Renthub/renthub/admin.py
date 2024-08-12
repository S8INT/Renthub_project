from django.contrib import admin
from .models import UserProfile, Property, Review, Message

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Property)
admin.site.register(Review)
admin.site.register(Message)
