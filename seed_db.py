import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed_database():
    print("Seeding database...")
    
    # Clear existing data
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Order.objects.all().delete()
    
    # Create customers
    customers = [
        Customer(name="Alice Johnson", email="alice@example.com", phone="+1234567890"),
        Customer(name="Bob Smith", email="bob@example.com", phone="123-456-7890"),
        Customer(name="Carol Davis", email="carol@example.com"),
    ]
    Customer.objects.bulk_create(customers)
    print(f"Created {len(customers)} customers")
    
    # Create products
    products = [
        Product(name="Laptop", price=999.99, stock=10),
        Product(name="Mouse", price=29.99, stock=50),
        Product(name="Keyboard", price=79.99, stock=30),
        Product(name="Monitor", price=299.99, stock=15),
    ]
    Product.objects.bulk_create(products)
    print(f"Created {len(products)} products")
    
    # Create orders
    alice = Customer.objects.get(email="alice@example.com")
    laptop = Product.objects.get(name="Laptop")
    mouse = Product.objects.get(name="Mouse")
    
    order = Order.objects.create(customer=alice)
    order.products.add(laptop, mouse)
    order.save()
    
    print(f"Created 1 order for {alice.name}")
    print("Database seeding complete!")

if __name__ == "__main__":
    seed_database()