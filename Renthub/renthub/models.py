from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=50)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    contact = models.CharField(max_length=15, blank=True)
    is_landlord = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Property(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255)
    image = models.ImageField(upload_to='property_images/')
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    

class Review(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    rating = models.PositiveBigIntegerField(default=1)
    comment = models.TextField()

    def __str__(self):
        return f'{self.reviewer.user.username} - {self.property.title}'
    

class Message(models.Model):
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_message')
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.sender.user.username} to {self.receiver.user.username}'
    