import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yogesh_inventory.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_users():
  if not User.objects.filter(username='admin_boss').exists():
    User.objects.create_superuser(
            username='admin_boss',
            email='admin@example.com',
            password='password123',
            role='admin',
            phone='9999999999',
            address='Admin Headquarters'
        )
    print("✅ Admin created!")
  # 2. 3 Vendors (Suppliers) Banana
  for i in range(1, 4):
      username = f'vendor_{i}'
      if not User.objects.filter(username=username).exists():
          User.objects.create_user(
              username=username,
              email=f'vendor{i}@test.com',
              password='password123',
              role='vendor',
              phone=f'888888880{i}',
              address=f'Vendor Street, Shop No {i}'
          )
          print(f"✅ Vendor {i} created!")
  # 3. 6 Customers Banana
  for i in range(1, 7):
    username = f'customer_{i}'
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(
            username=username,
            email=f'customer{i}@test.com',
            password='password123',
            role='customer',
            phone=f'777777770{i}',
            address=f'Customer House No {i}, Islapur'
        )
        print(f"✅ Customer {i} created!")

if __name__ == "__main__":
  print("🚀 Seeding users...")
  create_users()
  print("✨ Seeding completed successfully!")