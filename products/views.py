from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.conf import settings
import midtransclient
import datetime
import json
import uuid

from .models import Product, Category, Order, OrderItem


# ============================
# ✅ HOME
# ============================
def index(request):
    products = Product.objects.filter(is_active=True).exclude(image='')
    categories = Category.objects.all()

    return render(request, 'products/home.html', {
        'products': products,
        'categories': categories,
    })

# ============================
# ✅ LOGIN / LOGOUT
# ============================
def login_view(request):
    if request.session.get('is_authenticated'):
        return redirect('products:dashboard')

    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'login')
        
        if form_type == 'register':
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            password_confirm = request.POST.get('password_confirm', '')
            
            if not name or not email or not password:
                messages.error(request, '❌ Semua field harus diisi!')
                return render(request, 'products/login.html')
            
            if password != password_confirm:
                messages.error(request, '❌ Password tidak cocok!')
                return render(request, 'products/login.html')
            
            if len(password) < 6:
                messages.error(request, '❌ Password minimal 6 karakter!')
                return render(request, 'products/login.html')
            
            request.session['user_email'] = email
            request.session['user_name'] = name
            request.session['is_authenticated'] = True
            
            messages.success(request, f'✅ Akun berhasil dibuat! Selamat datang, {name}!')
            return redirect('products:dashboard')
        
        else:
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            remember = request.POST.get('remember', False)
            
            if not email or not password:
                messages.error(request, '❌ Email dan password harus diisi!')
                return render(request, 'products/login.html')
            
            request.session['user_email'] = email
            request.session['user_name'] = email.split('@')[0].capitalize()
            request.session['is_authenticated'] = True
            
            if remember:
                request.session.set_expiry(1209600)
            else:
                request.session.set_expiry(0)
            
            messages.success(request, f'✅ Selamat datang kembali, {request.session["user_name"]}!')
            return redirect('products:dashboard')

    return render(request, 'products/login.html')


def logout_view(request):
    user_name = request.session.get('user_name', 'User')
    request.session.flush()
    messages.success(request, f'👋 Sampai jumpa, {user_name}!')
    return redirect('products:login')


# ============================
# ✅ DASHBOARD
# ============================
def dashboard(request):
    if not request.session.get('is_authenticated'):
        return redirect('products:login')

    user_email = request.session.get('user_email')
    orders = Order.objects.filter(user_email=user_email).order_by('-created_at')
    total_orders = orders.count()
    total_spending = sum(float(o.total_amount) for o in orders) if total_orders > 0 else 0
    
    pending_orders = orders.filter(status='pending').count()
    paid_orders = orders.filter(status='paid').count()
    completed_orders = orders.filter(status='completed').count()
    cancelled_orders = orders.filter(status='cancelled').count()

    return render(request, 'products/dashboard.html', {
        'user_email': user_email,
        'user_name': request.session.get('user_name'),
        'orders': orders,
        'total_orders': total_orders,
        'total_spending': total_spending,
        'pending_orders': pending_orders,
        'paid_orders': paid_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
    })


# ============================
# ✅ CANCEL ORDER
# ============================
@require_POST
def cancel_order(request, order_id):
    if not request.session.get('is_authenticated'):
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=401)
    
    user_email = request.session.get('user_email')
    
    try:
        order = Order.objects.get(order_id=order_id, user_email=user_email)
        
        if order.status in ['pending', 'paid']:
            order.status = 'cancelled'
            order.save()
            
            for order_item in order.items.all():
                try:
                    if hasattr(order_item, 'product') and order_item.product:
                        if hasattr(order_item.product, 'stock'):
                            order_item.product.stock += order_item.quantity
                            order_item.product.save()
                except Exception as e:
                    print(f"⚠️ Stock restore error: {e}")
            
            messages.success(request, f'Order {order_id} berhasil dibatalkan.')
            return JsonResponse({'success': True, 'message': 'Order cancelled successfully'})
        else:
            messages.error(request, 'Order tidak bisa dibatalkan.')
            return JsonResponse({'success': False, 'message': 'Cannot cancel this order'}, status=400)
            
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Order not found'}, status=404)


# ============================
# ✅ VIEW ORDER DETAIL
# ============================
def order_detail(request, order_id):
    if not request.session.get('is_authenticated'):
        return redirect('products:login')
    
    user_email = request.session.get('user_email')
    order = get_object_or_404(Order, order_id=order_id, user_email=user_email)
    order_items = OrderItem.objects.filter(order=order)
    
    return render(request, 'products/order_detail.html', {
        'order': order,
        'order_items': order_items,
        'user_name': request.session.get('user_name'),
        'user_email': user_email,
    })


# ============================
# ✅ CART
# ============================
def cart(request):
    cart_items = request.session.get('cart', [])
    
    for item in cart_items:
        try:
            product = Product.objects.get(id=item['id'])
            if hasattr(product, 'stock'):
                item['stock'] = product.stock
        except Product.DoesNotExist:
            pass
    
    request.session['cart'] = cart_items
    request.session.modified = True
    
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    shipping = 15000 if subtotal > 0 else 0
    tax = subtotal * 0.10
    total = subtotal + shipping + tax
    
    return render(request, 'products/cart.html', {
        'cart_items': cart_items,
        'cart_count': len(cart_items),
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
    })


# ============================
# ✅ UPDATE CART QUANTITY
# ============================
def update_cart_quantity(request, product_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            change = data.get('change', 0)
            cart = request.session.get('cart', [])
            
            for item in cart:
                if item['id'] == product_id:
                    new_quantity = item['quantity'] + change
                    if new_quantity < 1:
                        new_quantity = 1
                    item['quantity'] = new_quantity
                    break
            
            request.session['cart'] = cart
            request.session.modified = True
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})


# ============================
# ✅ CHECKOUT - NO REDIRECT LOOP
# ============================
def checkout(request):
    if not request.session.get('is_authenticated'):
        return redirect('products:login')

    cart_items = request.session.get('cart', [])
    
    if not cart_items:
        messages.warning(request, '⚠️ Cart Anda kosong!')
        return redirect('products:cart')
    
    # Update stock info only (no blocking validation)
    for item in cart_items:
        try:
            product = Product.objects.get(id=item['id'])
            if hasattr(product, 'stock'):
                item['stock'] = product.stock
        except Product.DoesNotExist:
            pass
    
    request.session['cart'] = cart_items
    request.session.modified = True
    
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    shipping = 15000
    tax = subtotal * 0.10
    total = subtotal + shipping + tax

    if request.method == 'POST':
        shipping_method = request.POST.get('shipping_method', 'jne_regular')
        order_notes = request.POST.get('order_notes', '')
        full_name = request.POST.get('full_name', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        postal_code = request.POST.get('postal_code', '')
        province = request.POST.get('province', '')
        
        request.session['shipping_info'] = {
            'shipping_method': shipping_method,
            'order_notes': order_notes,
            'full_name': full_name,
            'phone': phone,
            'email': email,
            'address': address,
            'city': city,
            'postal_code': postal_code,
            'province': province,
        }
        
        request.session['order_total'] = float(total)
        request.session['order_subtotal'] = float(subtotal)
        request.session['order_shipping'] = float(shipping)
        request.session['order_tax'] = float(tax)
        
        print(f"✅ Checkout completed. Total: Rp {total:,.0f}")
        
        return redirect('products:payment')

    return render(request, 'products/checkout.html', {
        'user_email': request.session.get('user_email'),
        'user_name': request.session.get('user_name'),
        'cart_items': cart_items,
        'cart_count': len(cart_items),
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
    })


# ============================
# ✅ PAYMENT - NO REDIRECT LOOP
# ============================
def payment(request):
    if not request.session.get('is_authenticated'):
        messages.warning(request, 'Silakan login terlebih dahulu.')
        return redirect('products:login')

    order_total = request.session.get('order_total', 0)
    cart_items = request.session.get('cart', [])
    
    if not cart_items or order_total == 0:
        messages.warning(request, 'Cart Anda kosong!')
        return redirect('products:cart')
    
    order_id = "LOKA-" + str(uuid.uuid4())

    try:
        snap = midtransclient.Snap(
            is_production=True,
            server_key=settings.MIDTRANS_SERVER_KEY,
            client_key=settings.MIDTRANS_CLIENT_KEY,
        )

        param = {
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": int(order_total),
            },
            "customer_details": {
                "first_name": request.session.get("user_name", "Customer"),
                "email": request.session.get("user_email", "customer@loka.co"),
            },
        }

        transaction = snap.create_transaction(param)
        snap_token = transaction["token"]
        
        print(f"✅ Midtrans token created: {order_id}")

        order = Order.objects.create(
            user_email=request.session.get("user_email", "customer@loka.co"),
            user_name=request.session.get("user_name", "Customer"),
            order_id=order_id,
            total_amount=order_total,
            status="pending",
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product_name=item['name'],
                price=item['price'],
                quantity=item['quantity'],
                subtotal=item['price'] * item['quantity'],
            )

        request.session['current_order_id'] = order_id

        return render(request, "products/payment.html", {
            "snap_token": snap_token,
            "client_key": settings.MIDTRANS_CLIENT_KEY,
            "order_total": order_total,
            "order_id": order_id,
            "cart_items": cart_items,
            "items_count": len(cart_items),
        })

    except Exception as e:
        print(f"❌ PAYMENT ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, "Gagal memproses pembayaran. Silakan coba lagi.")
        return redirect('products:checkout')


# ============================
# ✅ PROCESSING
# ============================
def processing(request):
    if not request.session.get('is_authenticated'):
        return redirect('products:login')

    return render(request, 'products/processing.html', {
        'order_number': f"LOKA{request.session.session_key[:10]}",
        'amount': request.session.get('order_total', 0),
    })


# ============================
# ✅ SUCCESS PAGE
# ============================
def success(request):
    if not request.session.get('is_authenticated'):
        return redirect('products:login')
    
    order_id = request.session.get('current_order_id', None)
    order_total = request.session.get('order_total', 0)
    cart_items = request.session.get('cart', [])
    
    if order_id:
        try:
            order = Order.objects.get(order_id=order_id)
            order.status = "paid"
            order.save()
            
            for order_item in order.items.all():
                try:
                    if hasattr(order_item, 'product') and order_item.product:
                        if hasattr(order_item.product, 'stock'):
                            if order_item.product.stock >= order_item.quantity:
                                order_item.product.stock -= order_item.quantity
                                order_item.product.save()
                                print(f"✅ Stock decreased: {order_item.product.name}")
                except Exception as e:
                    print(f"⚠️ Stock decrease error: {e}")
            
            request.session['cart'] = []
            
        except Order.DoesNotExist:
            pass

    return render(request, 'products/success.html', {
        'order_number': order_id,
        'order_date': datetime.datetime.now().strftime('%d %B %Y, %H:%M'),
        'payment_method': 'Midtrans',
        'total_amount': order_total,
        'user_email': request.session.get('user_email'),
        'user_name': request.session.get('user_name'),
        'cart_items': cart_items,
    })


# ============================
# ✅ PRODUCT DETAIL
# ============================
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product_id)[:4]

    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })


# ============================
# ✅ CART – ADD
# ============================
def add_to_cart(request, product_id):
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            cart = request.session.get('cart', [])
            buy_now = request.POST.get('buy_now', False)

            found = False
            for item in cart:
                if item['id'] == product_id:
                    item['quantity'] += 1
                    found = True
                    break

            if not found:
                cart.append({
                    'id': product_id,
                    'name': product.name,
                    'price': float(product.price),
                    'quantity': 1,
                    'stock': product.stock if hasattr(product, 'stock') else 999,
                    'image': product.image.url if product.image else None,
                })

            request.session['cart'] = cart
            request.session.modified = True

            if buy_now:
                messages.success(request, f"✅ {product.name} ditambahkan ke keranjang!")
                return redirect('products:checkout')
            
            messages.success(request, f"✅ {product.name} ditambahkan ke keranjang!")
            return redirect('products:cart')

        except Product.DoesNotExist:
            messages.error(request, "❌ Produk tidak ditemukan!")

    return redirect('products:index')


# ============================
# ✅ CART – REMOVE
# ============================
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', [])
    cart = [i for i in cart if i['id'] != product_id]
    request.session['cart'] = cart
    request.session.modified = True

    messages.success(request, "Produk dihapus dari keranjang.")
    return redirect('products:cart')


# ============================
# ✅ CONTACT PAGE
# ============================
def contact(request):
    return render(request, 'products/contact.html')


# ============================
# ✅ CONTACT – SEND MESSAGE
# ============================
def send_contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        messages.success(request, "Pesan kamu berhasil dikirim!")
        return redirect('products:contact')

    messages.error(request, "Gagal mengirim pesan.")
    return redirect('products:contact')


# ============================
# 🔧 HELPER FUNCTIONS - TRACKING
# ============================
# TAMBAHKAN INI DI BAGIAN ATAS FILE views.py (setelah imports, sebelum def index)

from django.utils import timezone

def parse_user_agent(user_agent_string):
    """Parse user agent string untuk mendapatkan info browser, OS, device"""
    browser = "Unknown"
    os = "Unknown"
    device = "Desktop"
    
    if not user_agent_string:
        return browser, os, device
    
    # Detect Browser
    if "Chrome" in user_agent_string and "Edg" not in user_agent_string:
        browser = "Chrome"
    elif "Firefox" in user_agent_string:
        browser = "Firefox"
    elif "Safari" in user_agent_string and "Chrome" not in user_agent_string:
        browser = "Safari"
    elif "Edg" in user_agent_string:
        browser = "Edge"
    elif "Opera" in user_agent_string or "OPR" in user_agent_string:
        browser = "Opera"
    
    # Detect OS
    if "Windows" in user_agent_string:
        os = "Windows"
    elif "Mac OS" in user_agent_string:
        os = "MacOS"
    elif "Linux" in user_agent_string:
        os = "Linux"
    elif "Android" in user_agent_string:
        os = "Android"
        device = "Mobile"
    elif "iPhone" in user_agent_string or "iPad" in user_agent_string:
        os = "iOS"
        device = "Mobile" if "iPhone" in user_agent_string else "Tablet"
    
    return browser, os, device


def track_login(request, email, name):
    """Helper function untuk tracking login - FIXED VERSION"""
    try:
        # Ambil IP address
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
        
        # Ambil user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Parse user agent
        browser, os, device = parse_user_agent(user_agent)
        
        # Ambil atau create session key
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        
        # Simpan ke database
        from .models import LoginHistory
        LoginHistory.objects.create(
            user=None,  # Session-based auth tidak pakai Django User
            user_email=email,
            user_name=name,
            ip_address=ip_address,
            user_agent=user_agent,
            session_key=session_key,
            browser=browser,
            os=os,
            device=device
        )
        
        # Print untuk debugging
        print(f"✅ LOGIN TRACKED: {name} ({email}) dari {ip_address} - {browser} on {os}")
        
    except Exception as e:
        # Jangan sampai error tracking mengganggu login
        print(f"⚠️ Login tracking error: {e}")


def track_logout(email, session_key):
    """Helper function untuk tracking logout - FIXED VERSION"""
    try:
        from .models import LoginHistory
        
        # Cari login history terakhir yang belum logout
        login_record = LoginHistory.objects.filter(
            user_email=email,
            session_key=session_key,
            logout_time__isnull=True
        ).latest('login_time')
        
        # Update logout time
        login_record.logout_time = timezone.now()
        login_record.save()
        
        # Print untuk debugging
        duration = login_record.get_duration()
        print(f"🚪 LOGOUT TRACKED: {login_record.user_name} - Durasi: {duration}")
        
    except Exception as e:
        print(f"⚠️ Logout tracking error: {e}")


# ============================
# ✅ LOGIN / LOGOUT - WITH TRACKING (UPDATED)
# ============================
# GANTI function login_view dan logout_view dengan ini:

def login_view(request):
    if request.session.get('is_authenticated'):
        return redirect('products:dashboard')

    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'login')
        
        if form_type == 'register':
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            password_confirm = request.POST.get('password_confirm', '')
            
            if not name or not email or not password:
                messages.error(request, '❌ Semua field harus diisi!')
                return render(request, 'products/login.html')
            
            if password != password_confirm:
                messages.error(request, '❌ Password tidak cocok!')
                return render(request, 'products/login.html')
            
            if len(password) < 6:
                messages.error(request, '❌ Password minimal 6 karakter!')
                return render(request, 'products/login.html')
            
            request.session['user_email'] = email
            request.session['user_name'] = name
            request.session['is_authenticated'] = True
            
            # ✅ TRACKING LOGIN - REGISTER
            track_login(request, email, name)
            
            messages.success(request, f'✅ Akun berhasil dibuat! Selamat datang, {name}!')
            return redirect('products:dashboard')
        
        else:
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            remember = request.POST.get('remember', False)
            
            if not email or not password:
                messages.error(request, '❌ Email dan password harus diisi!')
                return render(request, 'products/login.html')
            
            name = email.split('@')[0].capitalize()
            request.session['user_email'] = email
            request.session['user_name'] = name
            request.session['is_authenticated'] = True
            
            if remember:
                request.session.set_expiry(1209600)
            else:
                request.session.set_expiry(0)
            
            # ✅ TRACKING LOGIN
            track_login(request, email, name)
            
            messages.success(request, f'✅ Selamat datang kembali, {name}!')
            return redirect('products:dashboard')

    return render(request, 'products/login.html')


def logout_view(request):
    user_name = request.session.get('user_name', 'User')
    user_email = request.session.get('user_email', '')
    session_key = request.session.session_key
    
    # ✅ TRACKING LOGOUT
    if user_email and session_key:
        track_logout(user_email, session_key)
    
    request.session.flush()
    messages.success(request, f'👋 Sampai jumpa, {user_name}!')
    return redirect('products:login')