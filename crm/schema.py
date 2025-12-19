import graphene
from graphene_django import DjangoObjectType
from django.core.exceptions import ValidationError
from django.db import transaction
import re
from .models import Customer, Product, Order

# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock", "created_at")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# Mutation: Create Customer
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)
    
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    
    def mutate(self, info, input):
        try:
            # 1. Validate email uniqueness
            if Customer.objects.filter(email=input.email).exists():
                raise Exception("Email already exists")
            
            # 2. Validate phone format (FIXED - no self.validate_phone call)
            if input.phone:
                # Phone validation regex
                import re
                pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
                if not re.match(pattern, input.phone):
                    raise Exception("Phone must be in format: +1234567890 or 123-456-7890")
            
            # 3. Create and save customer
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone if input.phone else None
            )
            customer.full_clean()
            customer.save()
            
            return CreateCustomer(
                customer=customer, 
                message="Customer created successfully"
            )
            
        except Exception as e:
            raise Exception(str(e))
        

# Mutation: Bulk Create Customers
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(CustomerInput, required=True)
    
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, inputs):
        customers = []
        errors = []
        import re
        
        for index, input_data in enumerate(inputs):
            try:
                # Validate email uniqueness
                if Customer.objects.filter(email=input_data.email).exists():
                    errors.append(f"Row {index+1}: Email '{input_data.email}' already exists")
                    continue
                
                # Validate phone
                if input_data.phone:
                    pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
                    if not re.match(pattern, input_data.phone):
                        errors.append(f"Row {index+1}: Invalid phone format")
                        continue
                
                # Create customer
                customer = Customer(
                    name=input_data.name,
                    email=input_data.email,
                    phone=input_data.phone
                )
                customer.full_clean()
                customer.save()
                customers.append(customer)
                
            except Exception as e:
                errors.append(f"Row {index+1}: {str(e)}")
        
        return BulkCreateCustomers(customers=customers, errors=errors)

# Mutation: Create Product
class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)
    
    product = graphene.Field(ProductType)
    
    def mutate(self, info, input):
        try:
            # Validate price is positive
            if input.price <= 0:
                raise ValidationError("Price must be positive")
            
            # Validate stock is not negative
            stock = input.stock if input.stock is not None else 0
            if stock < 0:
                raise ValidationError("Stock cannot be negative")
            
            product = Product(
                name=input.name,
                price=input.price,
                stock=stock
            )
            product.full_clean()
            product.save()
            
            return CreateProduct(product=product)
        except ValidationError as e:
            raise Exception(str(e))

# Mutation: Create Order
class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)
    
    order = graphene.Field(OrderType)
    
    def mutate(self, info, input):
        try:
            # Validate customer exists
            try:
                customer = Customer.objects.get(pk=input.customer_id)
            except Customer.DoesNotExist:
                raise ValidationError(f"Customer with ID {input.customer_id} does not exist")
            
            # Validate products exist
            products = []
            for product_id in input.product_ids:
                try:
                    product = Product.objects.get(pk=product_id)
                    products.append(product)
                except Product.DoesNotExist:
                    raise ValidationError(f"Product with ID {product_id} does not exist")
            
            # Validate at least one product
            if not products:
                raise ValidationError("At least one product is required")
            
            # Calculate total amount
            total_amount = sum(product.price for product in products)
            
            # Create order
            order = Order(customer=customer, total_amount=total_amount)
            if input.order_date:
                order.order_date = input.order_date
            order.save()
            order.products.set(products)
            
            return CreateOrder(order=order)
        except ValidationError as e:
            raise Exception(str(e))

# Query Class for CRM
class CRMQuery(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)
    
    def resolve_all_customers(self, info):
        return Customer.objects.all()
    
    def resolve_all_products(self, info):
        return Product.objects.all()
    
    def resolve_all_orders(self, info):
        return Order.objects.all()

# Mutation Class for CRM
class CRMMutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()