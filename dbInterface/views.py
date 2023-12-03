from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Customer, Order, Department, Cart, CartItem
from django.views.generic import DetailView, ListView
from .forms import LoginForm, CheckoutForm
from django.utils.timezone import now
from django.db.models import Q

'''Cassie To Do: 
    - Populate database. you can add pictures if you feel like it but idc 
    - Add payment method to Orders model, Checkout Form, and Checkout view
    - If you dont like the way any of the code is written u can change it 
    - Create ER Diagram '''

'''Sign Up and Login methods came from Django documentation and Codemy YouTube video. Changes made from documentation: 
    1. Sign Up creates a Customer instance
    2. The redirects were changed to fit the URLs'''


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            customer = Customer.objects.create(user=user, fname='', lname='')
            login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/sign_up.html', {'form': form})


def login_user(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("products")
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid form submission")
    else:
        form = LoginForm()

    return render(request, "registration/login.html", {"form": form})


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You Were Logged Out")
    else:
        messages.info(request, "You are already logged out.")
    return redirect('products')

#Searches (queries) the products listed
def search_results_view(request):
    if request.method == "POST":
        searched = request.POST['searched']
        products = Product.objects.filter(
            Q(productID__icontains=searched) |
            Q(depID__name__icontains=searched) |  # Use the appropriate field for Department name
            Q(name__icontains=searched) |
            Q(description__icontains=searched) |
            Q(price__icontains=searched)
        )
        return render(request, 'search_results.html', {'searched':searched, 'products':products})
        
    else:
        return render(request, 'search_results.html', {})

# Lists all the products on the "home" page
class AllProducts(ListView):
    model = Product
    template_name = "all_products.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch all departments
        context['departments'] = Department.objects.all()

        # Get the selected department from the request's GET parameters
        selected_department_id = self.request.GET.get('department')

        # Fetch products based on the selected department
        if selected_department_id:
            selected_department = get_object_or_404(Department, depID=selected_department_id)
            context['object_list'] = Product.objects.filter(depID=selected_department)
            context['selected_department'] = selected_department
        else:
            context['selected_department'] = None

        return context


# Shows individual product. Description, price, and has option to add to cart
class ProductDetail(DetailView):
    model = Product
    template_name = 'product_detail.html'


#
def cart(request):
    # Get the customer
    user = request.user
    customer = get_object_or_404(Customer, user=user)

    # if cart exists, retrieve it
    try:
        customer_cart = Cart.objects.get(customerID=customer)

    # If cart does not exist, create it
    except Cart.DoesNotExist:
        # Create cart
        customer_cart = Cart.objects.create(customerID=customer)

    # Get all the CartItems in the customer's cart
    cart_items = CartItem.objects.filter(cart=customer_cart)

    # Calculate cost
    cost = 0
    for item in cart_items:
        cost += item.product.price * item.quantity

    # Get info together to pass to HTML file
    context = {
        'cart_items': cart_items,
        'total_cost': cost,
    }

    # Pass info to HTML file and render the page
    return render(request, 'cart.html', context)


# Could change pk to product_ID
def add_to_cart(request, pk):
    # Get the product being added to cart
    product = get_object_or_404(Product, pk=pk)

    # Get customer adding the product
    user = request.user
    customer = get_object_or_404(Customer, user=user)

    try:
        # If customer's cart exists, get the cart
        customer_cart = Cart.objects.get(customerID=customer)

        try:
            # If the product is already in the cart, get it
            cart_item = CartItem.objects.get(cart=customer_cart, product=product)
            # Increment the quanity of the product
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            # If the product is not already in the cart, create it as a CartItem
            cart_item = CartItem.objects.create(cart=customer_cart, product=product, quantity=1)

    # If cart has not been created
    except Cart.DoesNotExist:
        # Create the cart
        customer_cart = Cart.objects.create(customerID=customer)
        # Create the CartItem for the product
        cart_item = CartItem.objects.create(cart=cart, product=product, quantity=1)

    # Tell customer the product was added
    messages.success(request, 'Product has been added to your cart.')

    return redirect('product_detail', pk=pk)


def remove_from_cart(request, product_id):
    # Get product and customer
    product = get_object_or_404(Product, pk=product_id)
    customer = get_object_or_404(Customer, user=request.user)

    try:
        # Get the customers cart
        customer_cart = Cart.objects.get(customerID=customer)
        # Get the CartItem holding the product
        cart_item = CartItem.objects.get(cart=customer_cart, product=product)

        # If there is more than one of the products, decrement the quantity of it's CartItem by 1
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()

        # If there is only 1 of the product in the cart, delete the CartItem completely
        else:
            cart_item.delete()

        # Tell the customer the product was removed
        messages.success(request, 'Product has been removed from your cart.')

    # In case the customer tries to remove an item that is not even the in the cart
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        messages.error(request, 'Product could not be removed from your cart.')

    return redirect('cart')


def checkout(request):
    # Get customer checking out
    user = request.user
    customer = get_object_or_404(Customer, user=user)

    # Get customer's Cart and CartItems
    customer_cart = Cart.objects.get(customerID=customer)
    cart_items = CartItem.objects.filter(cart=customer_cart)

    # Calculate the total cost of the items in the cart
    total_cost = sum(item.product.price * item.quantity for item in cart_items)

    # Use form so the customer can input billing, shipping, and payment**
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Get user input for billing and shipping. ADD PAYMENT HERE AFTER ADDED TO THE MODEL
            billing_address = form.cleaned_data['billing_address']
            shipping_address = form.cleaned_data['shipping_address']
            card = form.cleaned_data['card']
            # Each CartItem is ordered individually
            for cart_item in cart_items:
                Order.objects.create(
                    customerID=customer,
                    productID=cart_item.product,
                    quantity=cart_item.quantity,
                    billing_add=billing_address,
                    shipping_add=shipping_address,
                    card=card,
                    date=now()
                )

            # Delete cart after all orders are completed
            cart_items.delete()

            # Tell customer order was place
            messages.success(request, 'Checkout successful. Your order has been placed.')

            return redirect('cart')
    # If form was not filled out correctly, they try again
    else:
        form = CheckoutForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'total_cost': total_cost,
    }

    return render(request, 'checkout.html', context)

def orders(request):
    user = request.user
    customer = get_object_or_404(Customer, user=user)
    orders = Order.objects.filter(customerID=customer)

    context = {
        'orders': orders,
    }

    return render(request, 'orders.html', context)
    