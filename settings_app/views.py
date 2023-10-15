from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ChatSettings
from .serializers import ChatSettingsSerializer

class ChatSettingsCreateView(generics.CreateAPIView):
    queryset = ChatSettings.objects.all()
    serializer_class = ChatSettingsSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ChatSettingsUpdateView(generics.UpdateAPIView):
    queryset = ChatSettings.objects.all()
    serializer_class = ChatSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return ChatSettings.objects.get(user=user)

