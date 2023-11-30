from rest_framework import serializers
from .models import *

class  GeographySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default = serializers.CurrentUserDefault()
    )

    class Meta:
        model = Geopraphical_Location
        fields = "__all__"
    
