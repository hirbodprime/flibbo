from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from marketplace.models import NftProductModel
from .serializers import (
    NftProductlistSerializer,NftProductCreateSerializer,
    NftProductGeterializer,NftProductSerializer,
    NftProductUpdateSerializer
    )

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from marketplace.models import NftProductModel,OrderNumber,PurchaseTestModel
from wallet.models import UsersNfts
from wallet.api.serializers import UsersNftsSerializer
from accounts.models import CustomUser

from decimal import Decimal
from django.http import JsonResponse
import plisio
import json  # Import the json module
import re

class CreatePaymentAPI(APIView):
    def post(self, request, id):
        try:
            client = plisio.PlisioClient(api_key='3FCDL8ON_OOFKfCT-qzQQ0GnQb6iu5uDdWvKbk3KFxYpXkVujz6YMGJJvz1nCP8T')

            user = CustomUser.objects.get(email=request.user.email)
            nft = NftProductModel.objects.get(id=id)
            order = OrderNumber.objects.get(id=1)
            order.order_number += 1
            order.save()
            order_e = PurchaseTestModel.objects.create(user=request.user, order_number=order.order_number, purchase_name=nft)

            first_invoice = client.invoice(plisio.CryptoCurrency.USDT, nft.title, order.order_number, nft.price, callback_url='http://core.flxdevpanel.com:8081/market/api/plisio-callback/')
            
            # Access the invoice URL from the invoice object
            invoice_url = first_invoice.invoice_url
            
            # Return the invoice_url as a JSON response
            return Response({'invoice_url': invoice_url})
        except Exception as e:
            return Response({'error': str(e)})


class PlisioCallback(APIView):
    def post(self, request):
        try:
            data = request.body.decode('utf-8')  # Convert bytes to string
            print(data)
            print('this is done')
            # Use regex to find and extract the order_number
            order_number_match = re.search(r'name="order_number"\r\n\r\n(.*?)\r\n', data)
            txn_id_match = re.search(r'name="txn_id"\r\n\r\n(.*?)\r\n', data)
            
            print('this is done1')
            if order_number_match:
                order_number = order_number_match.group(1)
                print(order_number)
                # txn_id = txn_id_match.group(1)
                transaction_id_match = re.search(r'name="status"\r\n\r\n(.*?)\r\n', data)
                if transaction_id_match:
                    transaction_id = transaction_id_match.group(1)
                    print('in transaction')
                    print(transaction_id)
                    if transaction_id == "completed" or transaction_id == "mismatch":
                        print('in transaction completed')
                        purchase_data = PurchaseTestModel.objects.get(order_number=order_number)
                        user = CustomUser.objects.get(email=purchase_data.user)
                        nft = NftProductModel.objects.get(title=purchase_data.purchase_name)
                        nfts_purchased = UsersNfts.objects.create(user=user, nft_product=nft,video=nft.video)
                        
                response_data = {'message': 'Callback received successfully', 'order_number': order_number}
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'order_number not found in data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Handle any exceptions that may occur while processing the callback data
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class PurchaseNFT(APIView):
    def post(self, request, nft_id, format=None):
        try:
            nft = NftProductModel.objects.get(pk=nft_id)
        except NftProductModel.DoesNotExist:
            return Response({"error": "NFT not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if nft.bought_or_not:
            return Response({"error": "NFT has already been purchased"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user  # Assuming you're using authentication

        # Create a UsersNfts instance as a history purchase
        purchase = UsersNfts(user=user, nft_product=nft)
        purchase.save()

        # Update the NftProductModel to mark it as purchased
        nft.bought_or_not = True
        nft.save()

        # You can customize the response as needed
        response_data = {
            "message": f"Purchased {nft.title}",
            "purchase_details": UsersNftsSerializer(purchase).data,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)









class NftProductListView(generics.ListAPIView):
    queryset = NftProductModel.objects.all()
    serializer_class = NftProductlistSerializer
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Create a dictionary with a key for your data
        response_data = {'products': serializer.data}
        
        return Response(response_data)
        
class NftProductDetailView(generics.RetrieveAPIView):
    queryset = NftProductModel.objects.all()
    serializer_class = NftProductGeterializer


    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Custom data you want to include in the response
        custom_data = {
            "data":serializer.data
            # Add more custom data here as needed
        }
        return Response(custom_data, status=status.HTTP_200_OK)

class NftProductCreateView(generics.CreateAPIView):
    queryset = NftProductModel.objects.all()
    serializer_class = NftProductCreateSerializer

class NftProductUpdateView(generics.UpdateAPIView):
    queryset = NftProductModel.objects.all()
    serializer_class = NftProductUpdateSerializer
    def get(self, request, *args, **kwargs):
        instance = self.get_object()  # Get the instance you are updating
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
        
class NftProductDeleteView(generics.DestroyAPIView):
    queryset = NftProductModel.objects.all()
    serializer_class = NftProductSerializer
