from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import UserManagementViewSet,LogInView, LogOutView,NotificationViewSet
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'manage-users', UserManagementViewSet, basename='manage-users')
router.register(r'notifications', NotificationViewSet, basename='notifications')

urlpatterns = [
    path('', include(router.urls)),
    path('api/login/', LogInView.as_view(),name="token-obtain-pair"),
    path('api/login/refresh/',TokenRefreshView.as_view(),name='token-refresh'),
    path('api/logout/',LogOutView.as_view(),name="token-logout")
]