from .serializer import *
from .pagination import *
from .models import PastQuestion
from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

# Create your views here.

class UniversitiesViewSet(ModelViewSet):
    serializer_class = UniversityNameSerializer
    queryset = University.objects.all()
    permission_classes = [IsAdminUser]

class AdminPastQuestionViewSet(ModelViewSet):
    serializer_class = PastQuestionSerializer
    queryset = PastQuestion.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['university__name']
    filterset_fields = ['university']
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication]

    def get_serializer_context(self):
        return {'request': self.request}

class UserPastQuestionViewSet(ModelViewSet):
    serializer_class = PastQuestionSerializer
    queryset = PastQuestion.objects.all()
    filter_backends = [DjangoFilterBackend]
    # search_fields = ['university__name']
    filterset_fields = ['university']
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = DefaultPagination

    def get_serializer_context(self):
        return {'request': self.request}


    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            file_path = instance.past_question_file.path
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{instance.past_question_file.name}"'
                return response
        except Exception as error_message:
            return Response({'message': str(error_message)}, status=status.HTTP_404_NOT_FOUND)



    