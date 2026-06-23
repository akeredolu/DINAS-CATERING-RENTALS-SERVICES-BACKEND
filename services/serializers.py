from rest_framework import serializers
from .models import Order, OrderItem, Item

class OrderItemSerializer(serializers.ModelSerializer):
    # Let Django find the Item record using raw input ID integers
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())
    # Explicitly configure price as a standalone manual field to bypass naming loops
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ['item', 'quantity', 'is_by_dozen', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = [
            'order_number', 'client_name', 'client_email', 
            'client_phone', 'delivery_address', 'delivery_date', 
            'payment_method', 'payment_status', 'total_amount', 'items'
        ]

    def create(self, validated_data):
        # Extract item array lists from main dictionary payload blocks
        items_data = validated_data.pop('items')
        
        # Instantiate primary core order data layout rows
        order = Order.objects.create(**validated_data)
        
        # Unpack nested rows elements array sets
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            
        return order
