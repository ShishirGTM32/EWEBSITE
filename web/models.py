from django.contrib.auth.models import AbstractUser
from django.db import models

class Type(models.Model):
    type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=100, help_text="name of type")

    def __str__(self):
        return self.type_name


class Brand(models.Model):
    brand_id = models.AutoField(primary_key=True)
    brand_name = models.CharField(max_length=100, help_text="name of brand")

    def __str__(self):
        return self.brand_name


class Gender(models.Model):
    gender_id = models.AutoField(primary_key=True)
    gender_name = models.CharField(max_length=100, help_text="name of gender")

    def __str__(self):
        return self.gender_name


class Watch(models.Model):
    watch_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)  # Changed field name from brand_name to brand
    image_url = models.URLField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)  # Changed field name from gender_name to gender
    type = models.ForeignKey(Type, on_delete=models.CASCADE)  # Changed field name from type_name to type

    def __str__(self):
        return (
            f"Watch: {self.title}, "
            f"Brand: {self.brand.brand_name}, "  # Accessing the brand_name from the related Brand model
            f"Price: ${self.price:.2f}, "
            f"Image URL: {self.image_url}, "
            f"Gender: {self.gender.gender_name}, "  # Accessing the gender_name from the related Gender model
            f"Type: {self.type.type_name}"  # Accessing the type_name from the related Type model
        )

class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email})'


class User(AbstractUser):
    # Other custom fields for your user model (if needed)

    # Use related_name to avoid clashing with the default User model
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='web_user_set',  # Custom reverse accessor name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='web_user_permissions_set',  # Custom reverse accessor name
        blank=True
    )

    def __str__(self):
        return self.username