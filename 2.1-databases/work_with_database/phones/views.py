from django.shortcuts import render, redirect, get_object_or_404
from phones.models import Phone


def index(request):
    return redirect('catalog')

def show_catalog(request):
    template = 'catalog.html'
    sort_by = request.GET.get('sort', 'name')

    if sort_by == 'name':
        phones = Phone.objects.all().order_by('name')
    elif sort_by == 'price_asc':
        phones = Phone.objects.all().order_by('price')
    elif sort_by == 'price_desc':
        phones = Phone.objects.all().order_by('-price')
    elif sort_by == 'min_price': 
          phones = Phone.objects.all().order_by('price') 
    elif sort_by == 'max_price':
        phones = Phone.objects.all().order_by('-price')
    else:
        phones = Phone.objects.all()
    context = {'phones': phones, 'sort_by': sort_by}
    return render(request, template, context)


def show_product(request, slug):
    template = 'product.html'
    phone = get_object_or_404(Phone, name=slug)
    context = {'phone': phone}
    return render(request, template, context)
