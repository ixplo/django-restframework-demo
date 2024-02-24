from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import MenuItem, Category, Cart, Order, OrderItem

class CategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','slug','title']

class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['id','title','price','featured','category','category_id']
        
class CartSerializer (serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['user','menuitem','quantity','unit_price','price'] 
        
class OrderSerializer (serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['user','delivery_crew','status','total','date']
        
class OrderItemSerializer (serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['order','menuitem','quantity','unit_price','price']
        
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']