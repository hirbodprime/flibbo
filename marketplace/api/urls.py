from django.urls import path
from .views import (
    NftProductListView,
    NftProductDetailView,
    NftProductCreateView,
    NftProductUpdateView,
    NftProductDeleteView,
    PurchaseNFT,
    PlisioCallback,
    CreatePaymentAPI,
)

urlpatterns = [
    path('plisio-callback/', PlisioCallback.as_view(), name='plisio-callback'),
    path('create-payment/<int:id>/', CreatePaymentAPI.as_view(), name='create-payment'), 
    
    path('nfts/list/', NftProductListView.as_view(), name='nft-product-list'),
    path('nft/get/<int:pk>/', NftProductDetailView.as_view(), name='nft-product-detail'),
    path('nft/create/', NftProductCreateView.as_view(), name='nft-product-create'),
    path('nft/update/<int:pk>/', NftProductUpdateView.as_view(), name='nft-product-update'),
    path('nft/delete/<int:pk>/', NftProductDeleteView.as_view(), name='nft-product-delete'),

    path('purchase/<int:nft_id>/', PurchaseNFT.as_view(), name='purchase-nft'),

]
