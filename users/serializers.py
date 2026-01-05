from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User,Notification
import uuid
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserManagementSerializer(serializers.ModelSerializer):
    # Password optional rakha hai taaki vendor/customer ke liye skip ho sake
    password = serializers.CharField(
        write_only=True, 
        required=False, 
        allow_blank=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'phone', 'address', 'password'
        ]
        # Username ko optional rakhenge, email se auto-generate karenge agar nahi diya
        extra_kwargs = {'username': {'required': False}}

    def validate(self, data):
        role = data.get('role')
        password = data.get('password')

        # Logic: Agar role staff wala hai toh password compulsory hai
        staff_roles = ['admin', 'procurement', 'inventory', 'sales', 'finance']
        
        if role in staff_roles and not password:
            raise serializers.ValidationError({"password": f"Password is required for {role} role."})
            
        return data

    def create(self, validated_data):
        role = validated_data.get('role')
        email = validated_data.get('email')
        password = validated_data.pop('password', None)
        
        # Agar username nahi hai toh email ko hi username bana do
        if not validated_data.get('username'):
            validated_data['username'] = email if email else f"user_{uuid.uuid4().hex[:8]}"

        # User create karo
        if role in ['vendor', 'customer'] or not password:
            # Bina password wala user (Iska password set_unusable_password() ho jayega)
            user = User.objects.create(**validated_data)
            user.set_unusable_password() 
        else:
            # Login wala user (With Hashing)
            user = User.objects.create_user(**validated_data)
            user.set_password(password)
        
        user.save()
        return user
    

class AdministrationTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['role']=user.role
        token['email']= user.email
        return token

    def validate(self, attrs):
        data=super().validate(attrs)
        data['role']=self.user.role
        data['user_id'] = self.user.id
        return data
        
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Purana password sahi nahi hai.")
        return value
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'priority', 'is_read', 'action_url', 'created_at'] 