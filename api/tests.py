from django.urls import reverse
from api.models import Product, User
from rest_framework.test import APITestCase
from rest_framework import status


class ProductAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin', password='adminpass')
        self.normal_user = User.objects.create_user(
            username='user', password='userpass')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=10.00,
            stock=10
        )
        self.url = reverse('product-detail', args=[self.product.id])

    def test_get_product(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Test Product')

    def test_unauthorized_user_delete_product(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_update_product(self):
        data = {"name": "Updated Product"}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_admin_can_delete_product(self):
        self.client.login(username='user', password='userpass')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(id=self.product.pk).exists())

        self.client.logout()
        self.client.login(username='admin', password='adminpass')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
