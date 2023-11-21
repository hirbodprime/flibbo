from rest_framework import serializers
from flibbo_base.models import Support

class SupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Support
        fields = '__all__'
        read_only_fields = ('user',)
