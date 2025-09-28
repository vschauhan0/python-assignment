from django.db import models

# Create your models here.
class Contact(models.Model):
    first_name = models.CharField(max_length = 30)
    last_name = models.CharField(max_length = 30)
    email = models.EmailField()
    content = models.TextField(max_length=300)