from rest_framework import viewsets, status,permissions
from rest_framework.response import Response
from .models import User,Notification
from .serializers import (UserManagementSerializer,AdministrationTokenObtainPairSerializer,ChangePasswordSerializer,    NotificationSerializer)
from .permissions import IsSystemAdmin
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.decorators import action


class UserManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserManagementSerializer
    def get_permissions(self):
        if self.action in ['me', 'change_password']:
            return [permissions.IsAuthenticated()]

        return [IsSystemAdmin()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "status": "success",
                "message": f"User {user.username} created successfully as {user.role}",
                "data": {
                    "user_id": user.id,
                    "role": user.role,
                    "email": user.email
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({
                "status": "success",
                "message": "Password successfully updated."
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({
            "status": "success",
            "message": f"User {user.username} has been deactivated."
        }, status=status.HTTP_200_OK)
    
class LogInView(TokenObtainPairView):
    serializer_class = AdministrationTokenObtainPairSerializer
    
class LogOutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            # Token ko blacklist database mein daal do
            token.blacklist()

            return Response({
                "message": "Successfully logged out. Refresh token is now invalid."
            }, status=status.HTTP_200_OK)
            
        except TokenError:
            return Response({"error": "Token is invalid or already expired"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # SECURITY: Sirf logged-in user ke notifications filter karke do
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    # Ek extra feature: Sabhi notifications ko 'Read' mark karne ke liye
    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self):
        self.get_queryset().update(is_read=True)
        return Response({"status": "success", "message": "All notifications marked as read"})

    # Single notification ko 'Read' mark karne ke liye (/api/notifications/id/mark-read/)
    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "success", "message": "Notification marked as read"})