from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.warehouse.models import BaseModel

# Create your models here.

class CustomUser(BaseModel, AbstractUser):
    def profile_path(self, filename):
        pass
    
    username = None
    email = models.CharField(max_length= 70, unique= True)
    first_name = models.CharField(max_length= 25)
    middle_name = models.CharField(max_length= 25)
    last_name = models.CharField(max_length= 25)
    phone_number = models.BigIntegerField()
    profile_image = models.ImageField(upload_to= profile_path, default= '/'.join(['profiles', 'default', 'default.jpeg']))
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
