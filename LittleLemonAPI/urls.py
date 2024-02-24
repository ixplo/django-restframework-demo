from django.urls import path
from . import views

ALL = {'get': 'list', 'post': 'create'}
SINGLE = {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}

urlpatterns = [
    path('categories', views.CategoriesView.as_view()),
    path('categories/<int:pk>', views.SingleCategoryView.as_view(ALL)),
    path('menu-items', views.MenuItemsView.as_view(ALL)),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('cart/menu-items', views.CartView.as_view()),
    path('cart/orders', views.OrderView.as_view()),
    path('orders/<int:pk>', views.SingleOrderView.as_view()),
    
    path('groups/manager/users', views.ManagerView.as_view()),
    path('groups/manager/users/<int:pk>', views.SingleManagerView.as_view()),
    path('groups/delivery-crew/users', views.DeliveryCrewView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.SingleDeliveryCrewView.as_view()),
]