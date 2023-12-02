from collections.abc import Iterable
from django.db import models
from user.models import *
from commerce.models import *
import uuid
from django.utils import timezone
# Create your models here.

POST_CHOICES = (
    ("public", "public"),
    ("private", "private")
)


class MediaPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)
    media  = models.FileField(upload_to='post_files/', blank=True, null=True)


class HashTagsPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)
    hash_tags = models.CharField(max_length=256, null=True, blank=True)



class PostMedia(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)
    media = models.FileField(upload_to='post_files/', blank=True, null=True)
    time_stamp = models.DateTimeField(default=timezone.now)
    content = models.CharField(max_length=250, null=True, blank=False)
    shares = models.IntegerField(default=0)
    comment_text = models.ManyToManyField("Comment")
    comment = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    love = models.IntegerField(default=0)
    dislike = models.IntegerField(default=0)
    other_reactions = models.IntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    post_type =  models.CharField(choices=POST_CHOICES, default="public")
    each_media = models.ManyToManyField(MediaPost)
    hashtags =  models.ManyToManyField(HashTagsPost)
    is_business_post = models.BooleanField(
        default=False, verbose_name='Business Post')
    is_personal_post = models.BooleanField(
        default=True, verbose_name='Personal Post')
    tagged_users_post = models.ManyToManyField(
        User, related_name="users_tag",blank=True)
    time_since = models.CharField(max_length=256, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prev_comment_count = self.comment
    
    
    def save(self, *args, **kwargs) -> None:

        return super().save(*args, **kwargs)
    



class CommentMedia(models.Model):
    post = models.ForeignKey(
        'Post', on_delete=models.CASCADE, null=True)
    media = models.FileField(upload_to='comment_files/', blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)


class PromotionPlan(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in days")

    def __str__(self):
        return self.name

class HashTags(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hashtag = models.CharField(max_length=250, blank=True, null=True)


class Tagged_User(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField(blank=True, null=True)
    content = models.TextField()
    timestamp = models.TimeField(auto_now_add=True)
    reaction = models.ForeignKey(
        'Reaction', on_delete=models.SET_NULL, null=True)
    comments = models.ForeignKey(
        'Comment', on_delete=models.SET_NULL, null=True, related_name='post_comments', blank= True)
    # product = models.ForeignKey(
    #     Product, on_delete=models.SET_NULL, null=True, blank=True)
    hashtag = models.TextField(default='', null=True, blank=True)
    is_business_post = models.BooleanField(
        default=False, verbose_name='Business Post')
    is_personal_post = models.BooleanField(
        default=True, verbose_name='Personal Post')
    # Define a ManyToManyField for tagged users
    tagged_users = models.ManyToManyField(
        User, related_name='tagged_in_posts', blank=True)
    


class SharePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    caption = models.TextField(blank=True, null=True)
    shared_post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='shares')
    timestamp = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    content = models.TextField()
    responses = models.ManyToManyField("Reply", related_name="commnts_to_reply")
    media = models.ManyToManyField(CommentMedia)
    reaction = models.ForeignKey(
        'Reaction', on_delete=models.SET_NULL, null=True)
    timestamp = models.TimeField(auto_now_add=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)



        


class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    content = models.TextField()
    reaction = models.ForeignKey(
        'Reaction', on_delete=models.SET_NULL, null=True)
    


class Reaction(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('love', 'Love'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('haha', 'Haha'),
        ('wow', 'Wow'),
        ('others', 'Others'),
    ]

    reaction_type = models.CharField(
        max_length=20, choices=REACTION_CHOICES, verbose_name='Reaction')


class Repost(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True)
    timestamp = models.TimeField(auto_now_add=True)
    reaction = models.ForeignKey(
        'Reaction', on_delete=models.SET_NULL, null=True)
    comments = models.ForeignKey(
        'Comment', on_delete=models.SET_NULL, null=True)


class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True)
    timestamp = models.TimeField(auto_now_add=True)


class PromotedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    promotion_plan = models.ForeignKey(PromotionPlan, on_delete=models.CASCADE)
    promotion_status = models.CharField(max_length=20, choices=[(
        'pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)



class AdvertCategory(models.Model):
    name = models.CharField(max_length=250, blank=True, null= True)

class Advert(models.Model):
    title = models.CharField(max_length=250, blank=True, null=True)
    category = models.ForeignKey(AdvertCategory, on_delete=models.CASCADE)
    duration = models.CharField(max_length=250, choices=DURATION_CHOICES)
    custom_duration_start = models.DateTimeField()
    custom_duration_end = models.DateTimeField()
    