from django.db import models
from user.models import *
from commerce.models import *
import uuid
# Create your models here.


class PostMedia(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)
    media = models.FileField(upload_to='post_files/', blank=True, null=True)

class CommentMedia(models.Model):
    media = models.FileField(upload_to='comment_files/', blank=True, null=True)



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
    post = models.ForeignKey(
        'Post', on_delete=models.SET_NULL, null=True)
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
    media = models.ForeignKey(CommentMedia, on_delete=models.CASCADE, blank= True, null= True)
    reaction = models.ForeignKey(
        'Reaction', on_delete=models.SET_NULL, null=True)
    timestamp = models.TimeField(auto_now_add=True)


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
    