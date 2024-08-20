from django.db import models
from django.contrib.auth.models import User


# UserProfile model to extend the built-in User model with additional attributes.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    contact = models.CharField(max_length=20, blank=True)
    is_landlord = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


# Property model to represent the properties listed by landlords.
class Property(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('condo', 'Condo'),
        ('studio', 'Studio'),
        ('others', 'Others'),
    ]

    title = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255)
    image = models.ImageField(upload_to='property_images/')
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='properties')
    city = models.CharField(max_length=50)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES, default='apartment')
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.title} in {self.city}'

    def average_rating(self):
        """Calculate the average rating of the property."""
        reviews = self.reviews.all()
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 2)
        return None


# Review model to allow tenants to leave reviews and ratings on properties.
class Review(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_reviews')
    rating = models.PositiveIntegerField(default=1)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reviewer.user.username} rated {self.property.title}'

    def is_positive(self):
        """Determine if a review is positive based on the rating."""
        return self.rating >= 2


# Message model to facilitate communication between tenants and landlords.
class Message(models.Model):
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_messages')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'Message from {self.sender.user.username} to {self.receiver.user.username}'

    def is_related_to_property(self, property_id):
        """Check if the message is related to a specific property."""
        return self.property.id == property_id
