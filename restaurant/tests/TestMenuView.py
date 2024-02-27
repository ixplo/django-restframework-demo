from django.test import TestCase, Client
from django.urls import reverse

from rest_framework.status import HTTP_200_OK

from ..models import Menu
from ..serializers import MenuSerializer

# TestCase class
class TestMenuView(TestCase):

  def setUp(self) -> None:
    self.client = Client()

    Menu.objects.create(title='Grilled Fish', price=9.99, inventory=6)
    Menu.objects.create(title='Chips', price=3.45, inventory=25)
    Menu.objects.create(title='Chicken Burger', price=8.75, inventory=5)

  def test_getall(self):
    response = self.client.get(reverse('menu'))
    self.assertEqual(response.status_code, HTTP_200_OK)

    menu = Menu.objects.all()
    serializer = MenuSerializer(menu, many=True)
    self.assertEqual(response.data, serializer.data)