from django.contrib.auth.models import AbstractUser
from django.db import models

# Type Model
class Type(models.Model):
    type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=100, help_text="Name of the watch type")

    def __str__(self):
        return self.type_name

# Brand Model
class Brand(models.Model):
    brand_id = models.AutoField(primary_key=True)
    brand_name = models.CharField(max_length=100, help_text="Name of the brand")

    def __str__(self):
        return self.brand_name

# Gender Model
class Gender(models.Model):
    gender_id = models.AutoField(primary_key=True)
    gender_name = models.CharField(max_length=100, help_text="Name of the gender")

    def __str__(self):
        return self.gender_name

# Watch Model
class Watch(models.Model):
    watch_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    image_url = models.URLField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"Watch: {self.title}, "
            f"Brand: {self.brand.brand_name}, "
            f"Price: ${self.price:.2f}, "
            f"Image URL: {self.image_url}, "
            f"Gender: {self.gender.gender_name}, "
            f"Type: {self.type.type_name}"
        )

# Contact Model
class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email})'

# Custom User Model
class User(AbstractUser):
    # The default AbstractUser class includes:
    # username, email, password, first_name, last_name, is_active, is_staff, is_superuser,
    # and date_joined fields. No need to define them unless customizing.
    def __str__(self):
        return self.username

# Order Model
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=255)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=255)
    email = models.EmailField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    def __str__(self):
        return f"Order #{self.id} by {self.user}"

    def get_order_items(self):
        return self.order_items.all()

    def calculate_total(self):
        total = sum(item.get_total_price() for item in self.get_order_items())
        self.total_price = total
        self.save()

# OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Watch, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

    def get_total_price(self):
        return self.price * self.quantity
