from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product
from .forms import ProductForm
from orders.cart import Cart

def home(request):
    products = Product.objects.order_by('-created_at')
    return render(request, 'shop/home.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required
def sell_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            prod = form.save(commit=False)
            prod.seller = request.user
            prod.save()
            messages.success(request, 'Product listed.')
            return redirect('shop:home')
    else:
        form = ProductForm()
    return render(request, 'shop/sell.html', {'form': form})

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = Cart(request)
    cart.add(product_id=product.id, price=float(product.price), title=product.title)
    messages.success(request, 'Added to cart.')
    return redirect('shop:product_detail', pk=pk)


def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/products.html', {'products': products})