from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from flibbo_base.models import Support
from .serializers import SupportSerializer

from django.core.mail import send_mail


# class SupportListCreateView(generics.ListCreateAPIView):
#     serializer_class = SupportSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Support.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         instance = serializer.save(user=self.request.user)
#         self.send_support_email(instance)


#     def send_support_email(self, support):
        
#         subject = f'New Support Request: {support.subject}'
#         message = f"""
#             From: {support.user.username}
#             Email: {support.user.email}
#             Subject: {support.subject}
#             Content: {support.content}
#             Created At: {support.created_at}
#         """
        
#         from_email = f'{support.user.email}'
#         to_email = 'hirbodprime@gmail.com'

#         send_mail(subject, message, from_email, [to_email])

class SupportListCreateView(generics.ListCreateAPIView):
    serializer_class = SupportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Support.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SupportDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SupportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Support.objects.filter(user=self.request.user)
