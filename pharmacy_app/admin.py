# pharmacy_app/admin.py
from django.contrib import admin

from ecom.models import Category, Medicine, Order, OrderItem, PriceHistory, InventoryTransaction

# Register models that logically belong to pharmacy_app admin
# (Even though they're now in separate apps, we register them here for convenience)



admin.site.register(Category)
admin.site.register(Medicine)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PriceHistory)
admin.site.register(InventoryTransaction)

