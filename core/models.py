from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    name = models.CharField(max_length=200)
    price = models.FloatField()
    description = models.TextField(blank=True)
    created_At = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models. EmailField( blank =True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    
    def __str__(self):
        return self.user.username

    