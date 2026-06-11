from django.urls import path

from .views import (
    CompletedOrderCountView,
    OfferDetailRetrieveView,
    OfferListCreateView,
    OfferRetrieveUpdateDestroyView,
    OrderCountView,
    OrderListCreateView,
    OrderRetrieveUpdateDestroyView
)

urlpatterns = [
    path(
        'offers/',
        OfferListCreateView.as_view(),
        name='offer-list'
    ),
    path(
        'offers/<int:pk>/',
        OfferRetrieveUpdateDestroyView.as_view(),
        name='offer-detail'
    ),
    path(
        'offerdetails/<int:pk>/',
        OfferDetailRetrieveView.as_view(),
        name='offerdetail-detail'
    ),
    path(
        'orders/',
        OrderListCreateView.as_view(),
        name='order-list'
    ),
    path(
        'orders/<int:pk>/',
        OrderRetrieveUpdateDestroyView.as_view(),
        name='order-detail'
    ),
    path(
        'order-count/<int:business_user_id>/',
        OrderCountView.as_view(),
        name='order-count'
    ),
    path(
        'completed-order-count/<int:business_user_id>/',
        CompletedOrderCountView.as_view(),
        name='completed-order-count'
    ),
]

