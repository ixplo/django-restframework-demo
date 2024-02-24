from statistics import quantiles
from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from .models import MenuItem, Category, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, CartSerializer, OrderSerializer, OrderItemSerializer, UserSerializer

class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SingleCategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def check_permissions(self, request):
        if request.method in ['GET']:
            self.permission_classes = [IsCustomerOrDeliveryCrew]
        else:
            self.permission_classes = [IsManager]
        return super().check_permissions(request)
    
class MenuItemsView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'category']
    filterset_fields = ['price', 'category']
    search_fields = ['title', 'category__title']
    
class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        if(self.request.method=='GET'):
            return []

        return [IsAuthenticated()]
    
class CartView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    
class OrderView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def check_permissions(self, request):
        self.permission_classes = [IsAuthenticated]
        return super().check_permissions(request)
    
    def get(self, request, *args, **kwargs):
        user = request.user
        if user_is_customer(self, request):
            self.queryset = self.queryset.filter(user=user)
        if user_is_delivery_crew(self, request):
            self.queryset = self.queryset.filter(delivery_crew=user)
        return super().get(request, *args, **kwargs)
    
    def post(self, request, **kwargs):
        user = request.user
        date = request.data['date']
        if date is None:
            return Response({'message': 'object not found'}, status=status.HTTP_404_NOT_FOUND)
        order = self.create_order(user, date)
        for cart_item in Cart.objects.filter(user=user):
            order_item = self.create_order_item_obj(order, cart_item)
            order.total += order_item.price
        order.save()
        Cart.objects.filter(user=user).delete()
        return Response(status=status.HTTP_201_CREATED)
    
    def create_order(self, user, date):
        return Order.objects.create(
            user = user,
            date = date,
            total = 0,
        )

    def create_order_item_obj(self, order, cart_item_obj):
        menuitem = cart_item_obj.menuitem
        quantity = cart_item_obj.quantity
        unit_price = cart_item_obj.price
        price = unit_price * quantity

        order_item_obj = OrderItem.objects.create(
            order = order,
            menuitem = menuitem,
            quantity = quantity,
            unit_price = unit_price,
            price = price, 
        )
        order_item_obj.save()
        return order_item_obj
    
class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
class OrderItemView(generics.ListCreateAPIView):
    model = OrderItem
    related_model = MenuItem
    queryset = model.objects.all()
    serializer_class = OrderItemSerializer
    ordering_fields = ['user', 'menuitem']
    search_fields = ['user', 'menuitem']
    filterset_fields = ['user', 'menuitem']
    
    def check_permissions(self, request):
        self.permission_classes = [IsCustomer]
         


    
class SingleOrderItemView(generics.RetrieveUpdateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class ManagerView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Manager').exclude(groups__name='SysAdmin')
    serializer_class = UserSerializer
    group_name = 'Manager'
    ordering_fields = ['username', 'first_name', 'last_name']
    search_fields = ['username', 'first_name', 'last_name']
    filterset_fields = ['username', 'first_name', 'last_name']

    def check_permissions(self, request):
        if request.method in ['POST', 'GET']:
            self.permission_classes = [IsManager]
        else:
            self.permission_classes = [IsSysAdmin]
        return super().check_permissions(request)
    
    def post(self, request):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
        else:
            return Response({"message": "Username is incorrect or not existed."}, status.HTTP_400_BAD_REQUEST)
        message = addToGroup(self, 'Manager', username, user)
        return Response({"message": message}, status.HTTP_201_CREATED) 


class SingleManagerView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.filter(groups__name='Manager').exclude(groups__name='SysAdmin')
    serializer_class = UserSerializer
    group_name = 'Manager'

    def check_permissions(self, request):
        if self.user_is_requested_user(request):
            self.permission_classes = [IsManager]
        elif request.method in ['GET']:
            self.permission_classes = [IsManager]
        else: self.permission_classes = [IsSysAdmin]
        return super().check_permissions(request)


class DeliveryCrewView(generics.ListAPIView):
    model = User
    queryset = User.objects.filter(groups__name='Delivery Crew').exclude(groups__name='SysAdmin').exclude(groups__name='Manager')
    serializer_class = UserSerializer
    group_name = 'Delivery Crew'
    ordering_fields = ['username', 'first_name', 'last_name']
    search_fields = ['username', 'first_name', 'last_name']
    filterset_fields = ['username', 'first_name', 'last_name']
    
    def check_permissions(self, request):
        self.permission_classes = [IsManager]
        
    def post(self, request):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
        else:
            return Response({"message": "Username is incorrect or not existed."}, status.HTTP_400_BAD_REQUEST)
        message = addToGroup(self, 'Delivery Crew', username, user)
        return Response({"message": message}, status.HTTP_201_CREATED) 
    

class SingleDeliveryCrewView(generics.RetrieveUpdateAPIView):
    model = User
    queryset = User.objects.filter(groups__name='Delivery Crew').exclude(groups__name='SysAdmin').exclude(groups__name='Manager')
    serializer_class = UserSerializer
    group_name = 'Delivery Crew'
    
    def check_permissions(self, request):
        self.permission_classes = [IsManager]
        
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            if not user.groups.filter(name='Manager'):
                self.queryset = self.queryset.filter(user=user)
            order_item_obj = self.queryset.get(pk=kwargs['pk'])
            serialized_object = self.serializer_class(order_item_obj)
            return Response(serialized_object.data, status=status.HTTP_200_OK)
        except self.model.DoesNotExist:
            return Response({'message': 'object not found'}, status=status.HTTP_404_NOT_FOUND)

class CartView(APIView):
    model = Cart
    queryset = model.objects.all()
    serializer_class = CartSerializer
    related_model = OrderItem

    def check_permissions(self, request):
        self.permission_classes = [IsCustomer]
        
    def get(self, request, *args, **kwargs):
        user = request.user
        cart_items = self.queryset.filter(user=user) 
        serialized_object = CartSerializer(cart_items, many=True)
        return Response(serialized_object.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user
        self.create_cart_item_obj(request, user)
        return Response({}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = request.user
        cart_items = self.queryset.filter(user=user)
        cart_items.delete()
        return Response({}, status=status.HTTP_200_OK)
        

    def create_cart_item_obj(self, request, user):
        quantity = request.data.get('quantity')
        quantity = 1 if quantity is None else int(quantity)
        menuitem_id = request.data.get('menuitem')
        menuitem = MenuItem.objects.get(pk=menuitem_id)
        unit_price = request.data.get('unit_price')
        price = unit_price * quantity

        cartItem = Cart.objects.create(
            user = user,
            menuitem = menuitem,
            quantity = quantity,
            unit_price = unit_price,
            price = price, 
        )
        cartItem.save()
        return cartItem
    

class PermissionBaseMixin(BasePermission):
    group = ''

    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated):
            return False
        if request.user.groups.filter(name=self.group):
            return True
        return False

class IsSysAdmin(PermissionBaseMixin):
    group = 'SysAdmin'
    
class IsManager(PermissionBaseMixin):
    group = 'Manager'


class IsDeliveryCrew(PermissionBaseMixin):
    group = 'Delivery Crew'


class IsCustomer(PermissionBaseMixin):
    group = ''

class IsCustomerOrDeliveryCrew(BasePermission):

    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated):
            return False
        if request.user.groups.filter(name='Customer'):
            return True
        if request.user.groups.filter(name='Delivery Crew'):
            return True
        return False
    
def user_in_group(request, group_name=''):
    return request.user.groups.filter(name=group_name).exists()

def user_is_customer(self, request):
    return user_in_group(request, group_name='Customer')

def user_is_delivery_crew(self, request):
    return user_in_group(request, group_name='Delivery Crew')

def user_is_manager(self, request):
    return user_in_group(request, group_name='Manager')

def addToGroup(self, groupName, username, user):
    group = Group.objects.get(name=groupName)
    group.user_set.add(user)
    return f'User {username} was set as {groupName}'