from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PurchaseRequestViewSet

# Router setup
router = DefaultRouter()
router.register(r'purchase-requests', PurchaseRequestViewSet, basename='purchase-request')

urlpatterns = [
    path('', include(router.urls)),
]