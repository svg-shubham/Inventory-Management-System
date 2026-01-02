from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"purchase-order",PurchaseOrderViewSet,basename='purchase-order')
router.register(r'sales-order', SalesOrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]