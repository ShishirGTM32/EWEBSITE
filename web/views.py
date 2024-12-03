from django.db import connection
from django.db.utils import OperationalError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import ContactForm, LoginForm, RegisterForm
from django.contrib import messages
from .models import Watch, Brand, Gender, Type, Order, OrderItem
from django.core.mail import send_mail
from django.conf import settings

def check_db_connection():
    try:
        connection.ensure_connection()
        return True
    except OperationalError:
        return False

# Home index view
def index(request):
    if check_db_connection():
        watches = Watch.objects.all()[:12]
        return render(request, 'index.html', {'watches': watches})
    else:
        return HttpResponse("Database connection failed. Please check your database settings.")

def about(request):
    return render(request, 'about.html')

# Contact template view
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact_thank_you')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})

def thank_you_view(request):
    return render(request, 'thank_you.html')

# Shop template views
def add_to_cart(request, watch_id):
    try:
        watch = Watch.objects.get(watch_id=watch_id)
    except Watch.DoesNotExist:
        return HttpResponse("Watch not found.", status=404)

    if 'cart' not in request.session:
        request.session['cart'] = {}

    cart = request.session['cart']

    if str(watch.watch_id) in cart:
        cart[str(watch.watch_id)]['quantity'] += 1
    else:
        cart[str(watch.watch_id)] = {
            'watch_id': watch.watch_id,  # Ensure watch_id is stored
            'name': watch.title,
            'price': float(watch.price),
            'image_url': watch.image_url,
            'quantity': 1,
        }

    request.session.modified = True
    return redirect('shop')


def shop_view(request):
    # Get all available brands, genders, and types for the filters
    brands = Brand.objects.all()
    genders = Gender.objects.all()
    types = Type.objects.all()

    # Get the selected filters from GET parameters
    selected_brand = request.GET.get('brand', None)
    selected_gender = request.GET.get('gender', None)
    selected_price_range = request.GET.get('price_range', None)
    selected_type = request.GET.get('type', None)

    # Start with all watches
    watches = Watch.objects.all()

    # Apply filters based on user selection
    if selected_brand:
        watches = watches.filter(brand__brand_name=selected_brand)

    if selected_gender:
        watches = watches.filter(gender__gender_name=selected_gender)

    if selected_price_range:
        # Split the price range into min and max values
        if selected_price_range == "0-50":
            watches = watches.filter(price__gte=0, price__lte=50)
        elif selected_price_range == "51-100":
            watches = watches.filter(price__gte=51, price__lte=100)
        elif selected_price_range == "101-200":
            watches = watches.filter(price__gte=101, price__lte=200)
        elif selected_price_range == "201-500":
            watches = watches.filter(price__gte=201, price__lte=500)
        elif selected_price_range == "500+":
            watches = watches.filter(price__gte=500)

    if selected_type:
        watches = watches.filter(type__type_name=selected_type)

    # Paginate the filtered list of watches
    paginator = Paginator(watches, 9)  # Show 9 watches per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass the context to the template
    context = {
        'watches': page_obj,
        'brands': brands,
        'genders': genders,
        'types': types,
        'selected_brand': selected_brand,
        'selected_gender': selected_gender,
        'selected_price_range': selected_price_range,
        'selected_type': selected_type,
    }

    return render(request, 'shop.html', context)

# Cart template
def cart_view(request):
    cart = request.session.get('cart', {})

    total_price = sum(
        float(item['price']) * int(item['quantity'])
        for item in cart.values()
    )

    return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})


def clear_cart(request):
    request.session['cart'] = {}
    return redirect('cart')

def checkout(request):
    return render(request, 'checkout.html')

# Login register templates
def login_register_view(request):
    if request.user.is_authenticated:
        return redirect('account')

    login_form = LoginForm(request.POST or None)
    register_form = RegisterForm(request.POST or None)

    if request.method == 'POST':
        if 'login' in request.POST:
            if login_form.is_valid():
                username = login_form.cleaned_data['username']
                password = login_form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('account')
                else:
                    messages.error(request, 'Invalid username or password.')
            else:
                messages.error(request, 'Please correct the errors below.')

        elif 'register' in request.POST:
            if register_form.is_valid():
                register_form.save()
                messages.success(request, 'Account created successfully!')
                return redirect('login_register')
            else:
                messages.error(request, 'Please correct the errors below.')

    return render(request, 'login_register.html', {
        'login_form': login_form,
        'register_form': register_form,
    })

@login_required
def account_view(request):
    user = request.user
    return render(request, 'account.html', {'user': user})

def logout_view(request):
    # Log out the user
    logout(request)
    # Redirect to the homepage or any other page you prefer
    return redirect('index')

# Checkout view
def checkout_view(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('shop')  # If no cart, redirect to shop

    # Calculate the total price of the cart
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())

    if request.method == 'POST':
        # Extract shipping information from the form
        shipping_address = request.POST.get('shipping_address')
        shipping_city = request.POST.get('shipping_city')
        shipping_postal_code = request.POST.get('shipping_postal_code')
        shipping_country = request.POST.get('shipping_country')
        email = request.POST.get('email')

        # Create the order
        order = Order.objects.create(
            user=request.user,  # Ensure request.user is an instance of User
            total_price=total_price,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_postal_code=shipping_postal_code,
            shipping_country=shipping_country,
            email=email
        )

        # Add items to the order
        for watch_id, item in cart.items():
            watch = Watch.objects.get(watch_id=watch_id)
            OrderItem.objects.create(
                order=order,
                product=watch,
                price=item['price'],
                quantity=item['quantity']
            )

        # Send order confirmation email
        send_confirmation_email(order)

        # Clear cart after order is placed
        del request.session['cart']

        # Redirect to order success page
        return redirect('order_success_view', order_id=order.id)

    context = {
        'cart': cart,
        'total_price': total_price
    }
    return render(request, 'checkout.html', context)

def send_confirmation_email(order):
    subject = f"Order Confirmation - Order #{order.id}"
    message = f"Thank you for your order!\n\nOrder Summary:\n\n"
    message += f"Order ID: {order.id}\n"
    message += f"Shipping Address: {order.shipping_address}\n"
    message += f"Payment Method: {order.payment_method}\n"
    message += f"Total Price: ${order.total_price}\n\n"
    message += "Items in your order:\n"

    for item in order.get_order_items():
        message += f"- {item.product.title} (x{item.quantity}) - ${item.price * item.quantity}\n"

    message += "\nThank you for shopping with us!"

    # Send email to the user
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        fail_silently=False,
    )

def order_success_view(request, order_id):
    # Retrieve the order using the order_id from the URL
    order = get_object_or_404(Order, id=order_id)

    # Render the success page with the order details
    return render(request, 'order_success.html', {'order': order})

def place_order(request):
    if request.method == "POST":
        # Ensure you're capturing all form fields properly
        shipping_address = request.POST.get('address')
        shipping_city = request.POST.get('city')
        shipping_postal_code = request.POST.get('postal_code')
        shipping_country = request.POST.get('country')
        payment_method = request.POST.get('payment_method')

        # Ensure that the required fields are not empty
        if not shipping_address:
            return HttpResponse("Shipping address is required.", status=400)

        # Get cart from session and calculate the total price
        cart = request.session.get('cart', {})
        total_price = sum(
            float(item['price']) * int(item['quantity'])
            for item in cart.values()
        )

        # Creating an order in the database
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_postal_code=shipping_postal_code,
            shipping_country=shipping_country,
            email=request.user.email,
            payment_method=payment_method,
        )

        # Optionally clear the cart after placing the order
        request.session['cart'] = {}

        # Redirect to the order success page, passing the order's ID
        return redirect('order_success', order_id=order.id)

    else:
        return HttpResponse("Invalid method.", status=405)