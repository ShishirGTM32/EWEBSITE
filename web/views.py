from django.db import connection
from django.db.utils import OperationalError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import ContactForm,LoginForm, RegisterForm
from django.contrib import messages
from .models import Watch,Brand, Gender

def check_db_connection():
    try:
        connection.ensure_connection()
        return True
    except OperationalError:
        return False

def index(request):
    if check_db_connection():
        watches = Watch.objects.all()[:12]
        return render(request, 'index.html', {'watches': watches})
    else:
        return HttpResponse("Database connection failed. Please check your database settings.")

def about(request):
    return render(request,'about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect('contact_thank_you')  # Redirect to a "Thank You" page
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})

def thank_you_view(request):
    return render(request, 'thank_you.html')

def add_to_cart(request, watch_id):
    try:
        watch = Watch.objects.get(watch_id=watch_id)
    except Watch.DoesNotExist:
        return HttpResponse("Watch not found.", status=404)

    # Initialize cart in session if not already
    if 'cart' not in request.session:
        request.session['cart'] = {}

    cart = request.session['cart']

    # If item already in cart, increase quantity
    if str(watch.watch_id) in cart:
        cart[str(watch.watch_id)]['quantity'] += 1
    else:
        # Add item to cart with quantity 1
        cart[str(watch.watch_id)] = {
            'name': watch.title,
            'price': float(watch.price),
            'image_url': watch.image_url,
            'quantity': 1,
        }

    # Save updated cart back to session
    request.session.modified = True

    # Redirect back to the shop page or cart page
    return redirect('shop')  # or 'cart' if you want to go directly to the cart


def cart_view(request):
    cart = request.session.get('cart', {})

    total_price = sum(
        float(item['price']) * int(item['quantity'])  # Ensure both are numeric
        for item in cart.values()
    )

    return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})

def clear_cart(request):
    """Clear the shopping cart."""
    # Assuming cart is stored in the session
    request.session['cart'] = {}  # Clear the cart by resetting it in the session
    return redirect('cart')  # Redirect back to the cart page after clearing

def checkout(request):
    """The view for the checkout page."""
    # You can add any logic for the checkout page here, such as handling form submissions or displaying cart items
    return render(request, 'checkout.html')


def login_register_view(request):
    if request.user.is_authenticated:
        return redirect('account')  # or 'home' based on where you want logged-in users to go

    login_form = LoginForm(request.POST or None)  # Initialize the login form
    register_form = RegisterForm(request.POST or None)  # Initialize the register form

    if request.method == 'POST':
        if 'login' in request.POST:
            # Handle Login Form submission
            if login_form.is_valid():
                username = login_form.cleaned_data['username']
                password = login_form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('account')  # Redirect after successful login
                else:
                    messages.error(request, 'Invalid username or password.')
            else:
                messages.error(request, 'Please correct the errors below.')

        elif 'register' in request.POST:
            # Handle Register Form submission
            if register_form.is_valid():
                register_form.save()
                messages.success(request, 'Account created successfully!')
                return redirect('login_register')  # Redirect after successful registration
            else:
                messages.error(request, 'Please correct the errors below.')

    return render(request, 'login_register.html', {
        'login_form': login_form,
        'register_form': register_form,
    })


def shop_view(request):
    # Get all brand names and gender options
    brands = Brand.objects.all()
    genders = Gender.objects.all()

    # Get selected filters from GET parameters
    selected_brand = request.GET.get('brand', None)
    selected_gender = request.GET.get('gender', None)

    # Filter watches based on selected brand and gender
    watches = Watch.objects.all()

    if selected_brand:
        # Filter by brand_name (related model field access)
        watches = watches.filter(brand__brand_name=selected_brand)

    if selected_gender:
        # Filter by gender_name (related model field access)
        watches = watches.filter(gender__gender_name=selected_gender)

    # Implement pagination
    paginator = Paginator(watches, 9)  # 9 watches per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'watches': page_obj,
        'brands': brands,
        'genders': genders,
        'selected_brand': selected_brand,
        'selected_gender': selected_gender,
    }

    return render(request, 'shop.html', context)


@login_required
def account_view(request):
    user = request.user
    return render(request, 'account.html', {'user': user})

def home():
    return render(request, 'index.html')

# View for logging out
def logout_view(request):
    logout(request)
    return redirect('login_register')
