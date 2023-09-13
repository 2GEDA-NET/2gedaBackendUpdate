from rest_framework import serializers
from .models import *

class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = '__all__'

class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ['reaction_type']

class CommentSerializer(serializers.ModelSerializer):
    reaction = ReactionSerializer()
    
    class Meta:
        model = Comment
        fields = '__all__'

class ReplySerializer(serializers.ModelSerializer):
    reaction = ReactionSerializer()
    
    class Meta:
        model = Reply
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    reaction = ReactionSerializer()
    media = PostMediaSerializer(required=False)  # Nested serializer for media upload
    comments = CommentSerializer(many=True)
    
    class Meta:
        model = Post
        fields = '__all__'
    
    def create(self, validated_data):
        media_data = validated_data.pop('media', None)
        post = Post.objects.create(**validated_data)

        if media_data:
            PostMedia.objects.create(post=post, **media_data)

        return post

class RepostSerializer(serializers.ModelSerializer):
    reaction = ReactionSerializer()
    comments = CommentSerializer(many=True)
    
    class Meta:
        model = Repost
        fields = '__all__'

class SavedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedPost
        fields = '__all__'

# class PostMediaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PostMedia
#         fields = ('image', )
