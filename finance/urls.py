from django.urls import path,include
from .views import TransactionViewset,PaymentLogViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'transactions', TransactionViewset)
router.register(r'payments', PaymentLogViewset)

urlpatterns = [
    path('', include(router.urls)),
]