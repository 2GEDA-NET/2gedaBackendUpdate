import datetime
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from user.models import UserProfile
from rest_framework.parsers import MultiPartParser, FormParser
from .models import *
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authentication import *
from rest_framework.generics import *
from rest_framework import status, permissions
from rest_framework.response import Response


class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = ChatMessage.objects.all()
    serializer_class = MessageSerializer

class StatusViewSet(viewsets.ModelViewSet):
    queryset = LifeStyle.objects.all()
    serializer_class = LifeStyleSerializer

class ThreadListView(ListAPIView):
    serializer_class = ThreadSerializer

    def get_queryset(self):
        # Filter threads by the currently authenticated user
        return Thread.objects.by_user(user=self.request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    

class StoryUploadAPI(APIView):
    permission_classes=[IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self,request):
        story_data=request.data.get('post_images')
        serializer=LifeStyleSerializer(data={'story':story_data,'user':request.user.id})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


             

# view story

class GetStories(APIView):
    permission_classes = [IsAuthenticated]

    def get (self,request):

        follower_ids = User.objects.filter(
        user=request.user).values_list('followed_user', flat=True)
        
        follow_data = LifeStyle.objects.filter(
            Q(user__in=follower_ids) | Q(user=request.user)).order_by('-id')

        if follow_data.count() > 0:
            serializer = LifeStyleSerializer(follow_data, many=True)
            data = serializer.data

            for post in data:
                post['image_url'] = request.build_absolute_uri(
                    post['story'])
                
            
            return Response({'data': data, 'message': 'data get', 'success': 1})
        else:
            return Response({'data': 'no data available'}, status=status.HTTP_400_BAD_REQUEST)


#viewed story
class ViewedLifeStyle(APIView):
    def get(self,request,story_id):
        queryset=LifeStyle.objects.get(pk=story_id)
        queryset.status=True
        queryset.save()
        serializer=LifeStyleSerializer(queryset)

        return Response(serializer.data)
    

# story delete
class LifeStyleDelete(APIView):
    def get(self,request):
        queryset=LifeStyle.objects.all()
        serializer=LifeStyleSerializer(queryset,many=True)
        data=serializer.data

        for post in data:

            post_time_str = post['date']
            post_time_obj = t.datetime.strptime(
                post_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')

            time_diff = datetime.now() - post_time_obj
            hours_diff = int(time_diff.total_seconds() // 3600)
            print(hours_diff)


            if hours_diff>=24:
                LifeStyle.objects.filter(id=post['id']).delete()

        return Response('LifeStyle deleted successfully')




# get single user lifestyle

class SingleUserLifeStyle(APIView):
    def get(self,request,user_id):
        queryset=LifeStyle.objects.filter(user=user_id)

        if queryset.count()>0:
            serializer=LifeStyleSerializer(queryset,many=True)
            data = serializer.data

            for post in data:
                post['image_url'] = request.build_absolute_uri(
                    post['lifestyle'])
                
            return Response(serializer.data)
        else:
            return Response({'data': 'no data available'}, status=status.HTTP_400_BAD_REQUEST)

    