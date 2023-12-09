from rest_framework import serializers

from user.serializers import UserSerializer
from .models import *
from django.utils.timesince import timesince
from datetime import datetime


class PostMediaSerializer_OAJ(serializers.ModelSerializer):
    user_profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = PostMedia
        fields = '__all__'

    def get_user_profile_image_url(self, obj):
        return obj.post.user.profileimage.image.url if obj.post.user.profileimage else None
    


class PostMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = MediaPost
        fields = ["user", "media"]


class ReactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(
        default = serializers.CurrentUserDefault()
    )
    class Meta:
        model = Reaction
        fields = '__all__'

    def to_internal_value(self, data):
        # Handle both serialized representation and instance
        if isinstance(data, Reaction):
            return data

        return super().to_internal_value(data)



class ReplySerializer(serializers.ModelSerializer):
    reaction = ReactionSerializer()
    user = UserSerializer(
        default = serializers.CurrentUserDefault()
    )

    class Meta:
        model = Reply
        fields = '__all__'


class CommentMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommentMedia
        fields = "__all__"        



class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(
        default = serializers.CurrentUserDefault()
    )
    reaction = ReactionSerializer(many=True, required=False)
    responses = ReplySerializer(many=True, required=False)
    media = CommentMediaSerializer(many=True, required=False)
    reaction_count = serializers.SerializerMethodField()
    responses_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = "__all__"

    def get_reaction_count(self, obj):
        if obj.reaction is not None:
            return obj.reaction.count()
        return None
    
    def get_responses_count(self, obj):
        if obj.responses is not None:
            return obj.responses.count()
        return None
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        return representation
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        time_instance = representation.get('time_stamp')
        
        time_object = datetime.strptime(time_instance, time_format)
        
        time_difference = datetime.now() - time_object
        
        time_since = timesince(time_object)
        
        data = {
            "time_since": time_since
        }
        representation.update(data)
        return representation
    


class HashTagSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = HashTagsPost
        fields = '__all__'


class SharePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharePost
        fields = '__all__'


class PostUserSerializer(serializers.ModelSerializer):

    work = serializers.CharField(source='userprofile.work', read_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'work']

class GetPostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ('id', 'media')  # Include other fields as needed




class PostSerializer(serializers.Serializer):
    user = PostUserSerializer()
    reaction = ReactionSerializer(required=False)
    # Nested serializer for media upload
    media = GetPostMediaSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, required=False)
    hashtag = HashTagSerializer(many=True, required=False)
    shares_count = serializers.SerializerMethodField()
    shares = SharePostSerializer(many=True, read_only=True)  # Add this line

    # class Meta:
    #     model = Post
    #     fields = '__all__'

    def get_shares_count(self, obj):
        return obj.shares.count()

    def create(self, validated_data):
        media_data = validated_data.pop('media', None)
        post = Post.objects.create(**validated_data)

        if media_data:
            PostMedia.objects.create(post=post, **media_data)

        return post

class NewPostMediaSerializer(serializers.ModelSerializer):
    post =  PostSerializer()

    class Meta:
        model = PostMedia
        fields = ["post","media" ]


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


class PromotedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotedPost
        fields = '__all__'


# class PostMediaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PostMedia
#         fields = ('image', )


# Define document file extensions

video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.ogg', '.3gp', '.mpeg', '.vob', '.divx',
                    '.rm', '.m4v', '.ts', '.m2ts', '.ogv', '.asf', '.mpg', '.mp2', '.m2v', '.mxf', '.mts', '.m2t', '.m1v', '.mpv']


class VideoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        # Serialize only if the associated file has a video extension
        if instance.file and any(instance.file.media.name.endswith(ext) for ext in video_extensions):
            return super().to_representation(instance)
        return None


# Define document file extensions
document_extensions = ['.pdf', '.doc', '.docx', '.txt', '.rtf']


class DocumentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        # Serialize only if the associated file has a document extension
        if instance.file and any(instance.file.media.name.endswith(ext) for ext in document_extensions):
            return super().to_representation(instance)
        return None


# Define audio file extensions
audio_extensions = ['.mp3', '.wav', '.ogg', '.aac', '.flac',
                    '.wma', '.m4a', '.opus', '.amr', '.mid', '.midi', '.ac3']


class AudioPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        # Serialize only if the associated file has an audio extension
        if instance.file and any(instance.file.media.name.endswith(ext) for ext in audio_extensions):
            return super().to_representation(instance)
        return None


image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']


class ImagePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        # Serialize only if the associated file has an image extension
        if instance.file and any(instance.file.media.name.endswith(ext) for ext in image_extensions):
            return super().to_representation(instance)
        return None


others_extensions = ['.exe', '.msi', '.pkg', '.deb', '.rpm', '.dmg', '.zip', '.app', '.apk', '.jar', '.rar', '.7z', '.tar.gz', '.tgz',
                     '.tar.bz2', '.tbz2', '.tar', '.cab', '.sit', '.sitx', '.zipx', '.z', '.lzh', '.lha', '.ace', '.arj', '.gz', '.bz2', '.xz', '.zst']


class OtherPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        # Serialize only if the associated file has an image extension
        if instance.file and any(instance.file.media.name.endswith(ext) for ext in others_extensions):
            return super().to_representation(instance)
        return None



class CreatePostSerializer(serializers.ModelSerializer):
    user = UserSerializer(
        default = serializers.CurrentUserDefault()
    )
    comment_text = CommentSerializer(many=True, required=False)
    each_media = PostMediaSerializer(many=True, required=False)
    hashtags = HashTagSerializer(many=True, required=False)
    content =  serializers.CharField(required=False)
    Reaction = ReactionSerializer(many=True, required=False)
    post_reaction_count = serializers.SerializerMethodField()
    post_comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PostMedia
        fields = "__all__"

    def validate(self, attrs):
        error = {}
        if attrs.get("content") == None and attrs.get("media") == None:
            error["error"] = "You have to post a media or text"

            raise serializers.ValidationError(error)
        return super().validate(attrs)
    
    
    def get_post_reaction_count(self, obj):
        if obj.comment_text.exists() and  obj.Reaction.exists():
            return sum(comment.reaction.count() for comment in obj.comment_text.all()) + obj.Reaction.count()
                
        elif obj.Reaction is not None :
            return (obj.Reaction.count())
        
        return None
    
    def get_post_comment_count(self, obj):
        if obj.comment_text.exists():
            return sum(reply.responses.count() for reply in obj.comment_text.all()) + obj.comment_text.count()
        return None


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = representation.get("user")
        time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        time_instance = representation.get('time_stamp')
        
        time_object = datetime.strptime(time_instance, time_format)
        
        time_difference = datetime.now() - time_object
        
        time_since = timesince(time_object)
        
        data = {
            "time_since": time_since
        }
        representation.update(data)
        return representation
    
