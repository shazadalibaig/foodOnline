from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,JsonResponse
from vendor.models import Vendor,OpeningHour
from menu.models import Category,FoodItem
from django.db.models import Prefetch
from .models import cart
from marketplace.context_processors import get_cart_count,get_cart_amounts
from django.contrib.auth.decorators import login_required
from datetime import date




def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True,user__is_active=True)
    vendor_count = vendors.count()
    context = {'vendors':vendors,'vendor_count':vendor_count}
    return render(request,'marketplace/listings.html',context)

def vendor_detail(request,vendor_slug):
    vendor = get_object_or_404(Vendor,vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset = FoodItem.objects.filter(is_availabe=True)
        )
    )
    
    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day','-from_hour')
    
    today_date = date.today()
    today = today_date.isoweekday()
    
    current_day_opening_hours = OpeningHour.objects.filter(vendor=vendor,day=today)
    
    if request.user.is_authenticated:
        cart_items = cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {'vendor':vendor,'categories':categories,'cart_items':cart_items,'opening_hours':opening_hours,'current_day_opening_hours':current_day_opening_hours}
    return render(request,'marketplace/vendor_detail.html',context)

def add_to_cart(request,food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #check if the fooditem exists
            try:
                fooditems = FoodItem.objects.get(id=food_id)
                #check whether the food item already exists in the cart
                try:
                    checkcart = cart.objects.get(user=request.user,fooditems=fooditems)
                    #increase the cart
                    checkcart.quantity += 1
                    checkcart.save()
                    return JsonResponse({'status':'success','message':'Increased the cart successfully','cart_counter':get_cart_count(request),'qty':checkcart.quantity,'cart_amount':get_cart_amounts(request)})
                except:
                    checkcart = cart.objects.create(user=request.user,fooditems=fooditems,quantity=1)
                    return JsonResponse({'status':'success','message':'Added to the cart successfully','cart_counter':get_cart_count(request),'qty':checkcart.quantity,'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status':'failed','message':'This food does not exists'})
        else:
            return JsonResponse({'status':'failed','message':'Invalid Request!'})
    else:
        return JsonResponse({'status':'login_required','message':'Please login to continue'})
    
    
def decrease_cart(request,food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #check if the fooditem exists
            try:
                fooditems = FoodItem.objects.get(id=food_id)
                #check whether the food item already exists in the cart
                try:
                    checkcart = cart.objects.get(user=request.user,fooditems=fooditems)
                    if checkcart.quantity > 1:
                        checkcart.quantity -= 1
                        checkcart.save()
                    else:
                        checkcart.delete()
                        checkcart.quantity = 0
                    return JsonResponse({'status':'success','cart_counter':get_cart_count(request),'qty':checkcart.quantity,'cart_amount':get_cart_amounts(request)})
                except:
                    return JsonResponse({'status':'failed','message':'You dont have any items in your cart'})
            except:
                return JsonResponse({'status':'failed','message':'This food does not exists'})
        else:
            return JsonResponse({'status':'failed','message':'Invalid Request!'})
    else:
        return JsonResponse({'status':'login_required','message':'Please login to continue'})

@login_required(login_url='/login')
def cartview(request):
    cart_items = cart.objects.filter(user=request.user).order_by('created_at')
    context = {'cart_items':cart_items}
    return render(request,'marketplace/cart.html',context)    

def delete_cart(request,cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                cart_item = cart.objects.get(user=request.user,id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status':'success','message':'Cart item has been deleted','cart_counter':get_cart_count(request),'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status':'failed','message':'Cart item does not exist'})
        else:
            return JsonResponse({'status':'failed','message':'Invalid Request!'})
        

def search(request):
    keyword = request.GET['keyword']
    radius = request.GET['radius']
    
    vendors = Vendor.objects.filter(vendor_name__icontains=keyword,is_approved=True,user__is_active=True)
    print(vendors)
    return render(request,'marketplace/listings.html')
    