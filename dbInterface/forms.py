from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


# Add payment in this after it is added to the model
class CheckoutForm(forms.Form):
    billing_address = forms.CharField(label='Billing Address', max_length=255)
    shipping_address = forms.CharField(label='Shipping Address', max_length=255)