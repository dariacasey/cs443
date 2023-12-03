from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.user}"


class Department(models.Model):
    depID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    productID = models.AutoField(primary_key=True)
    depID = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"{self.name}"

# They way I have set this up is there is an individual order for every product. If a user orders multiples of the same
# product, then those will be in the same order. there is 1 order per CartItem.
# Add payment to this model
class Order(models.Model):
    orderID = models.AutoField(primary_key=True)
    customerID = models.ForeignKey(Customer, on_delete=models.CASCADE)
    productID = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    billing_add = models.CharField(max_length=255)
    shipping_add = models.CharField(max_length=255)
    card = models.PositiveIntegerField(default=0000000000000000)
    date = models.DateField()

    def __str__(self):
        return f"Order {self.orderID} | {self.date} | {self.customerID}"



# Cart is in quotations because since it comes after this model, it thinks it doesn't exist. I put this model after Cart,
# but then CartItem would have had to be in quotations
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    def __str__(self):
        return f"{self.product.name} | {self.quantity}x | {self.cart.customerID.user}"


class Cart(models.Model):
    cartID = models.AutoField(primary_key=True)
    customerID = models.ForeignKey(Customer, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product, through=CartItem)
    quantity = models.PositiveIntegerField(default=1)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    def __str__(self):
        return f"{self.customerID.user}'s Cart"

