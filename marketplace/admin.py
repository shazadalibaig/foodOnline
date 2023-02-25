from django.contrib import admin
from . models import cart

# Register your models here.

class CartAdmin(admin.ModelAdmin):
    list_display = ('user','fooditems','quantity','updated_at')


admin.site.register(cart,CartAdmin)
