from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from wallet.models import UsersNfts
from .serializers import UsersNftsSerializer




class UsersNftsList(APIView):
    def get(self, request, format=None):
        purchases = UsersNfts.objects.filter(user=request.user)
        serializer = UsersNftsSerializer(purchases, many=True,context={'request':request})
        reponse_data = {
            'purchase-history':serializer.data
        }
        return Response(reponse_data)
