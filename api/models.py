from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    @property
    def in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.name


class User(AbstractUser):
    pass


class Order (models.Model):
    class StatusChoices (models.TextChoices):
        PENDING = 'Pending'
        CONFIRMED = 'Confirmed'
        CANCLED = 'Cancelled'
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10,
                              choices=StatusChoices.choices,
                              default=StatusChoices.PENDING)
    products = models.ManyToManyField(
        Product, through='OrderItem', related_name='orders')

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"


class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    # price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def item_subtotal(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.order_id}"
