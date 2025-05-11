from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.
from rest_framework import filters, generics, viewsets
from rest_framework.decorators import api_view
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import InStockFilter, OrderFilter, ProductFilter
from api.models import Order, OrderItem, Product
from api.serializers import (OrderSerializer, ProductInfoSerializer,
                             ProductSerializer)
from rest_framework.decorators import action


class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.order_by('pk')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,
                       InStockFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'stock']
    # make the default page size is in settings.py
    # pagination_class = LimitOffsetPagination
    pagination_class = PageNumberPagination
    pagination_class.page_size_query_param = 'size'
    pagination_class.page_size = 5
    pagination_class.max_page_size = 100

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    @action(detail=False,
            method=['get'], url_path='user-orders',
            )
    def user_orders(self, request):
        orders = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


# class OrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.prefetch_related('items__product')
#     serializer_class = OrderSerializer


# class UserOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.prefetch_related('items__product')
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         qs = super().get_queryset()
#         return qs.filter(user=self.request.user)


class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer(
            {'products': products,
             'count': len(products),
             'max_price': products.aggregate(max_price=Max('price'))['max_price']
             })
        return Response(serializer.data)
