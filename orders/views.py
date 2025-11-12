from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Order, OrderItem
from .cart import Cart
from shop.models import Product

@login_required
def cart_view(request):
    cart = Cart(request)
    return render(request, 'orders/cart.html', {'cart': list(cart), 'total': cart.total()})

@login_required
def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    messages.info(request, 'Item removed.')
    return redirect('orders:cart')

@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.clear()
    cart.add(product_id=product.id, price=float(product.price), title=product.title, quantity=1)
    return redirect('orders:checkout')

@login_required
def checkout(request):
    cart = Cart(request)
    if request.method == 'POST':
        # Dummy payment: always success
        total = Decimal(cart.total())
        order = Order.objects.create(user=request.user, total_amount=total, status='success')
        for item in cart:
            prod = Product.objects.get(id=item['id'])
            OrderItem.objects.create(order=order, product=prod, quantity=item['quantity'], price=item['price'])
            # naive stock decrement
            if prod.stock >= item['quantity']:
                prod.stock -= item['quantity']
                prod.save()
        cart.clear()
        messages.success(request, 'Order placed successfully.')
        return redirect('orders:order_list')
    return render(request, 'orders/checkout.html', {'cart': list(cart), 'total': cart.total()})

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/orders.html', {'orders': orders})
