from django.db import models
from user.models import *

# Create your models here.
class PostMedia(models.Model):
    media = models.FileField(upload_to= 'post_files/', blank = True, null = True)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    file = models.ForeignKey(PostMedia, on_delete = models.SET_NULL, null=True)
    content = models.TextField()
    timestamp = models.TimeField()
    reaction = models.ForeignKey('Reaction', on_delete = models.SET_NULL, null=True)
    comments = models.ForeignKey('Comment', on_delete = models.SET_NULL, null=True, related_name='post_comments')
    hashtag = models.CharField(max_length=250, blank=True)
    is_business_post = models.BooleanField(default = False, verbose_name = 'Business Post')
    is_personal_post = models.BooleanField(default = True, verbose_name = 'Personal Post')


class SharePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_post = models.ForeignKey('Post', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete = models.CASCADE, null=True)
    content = models.TextField()
    reaction = models.ForeignKey('Reaction', on_delete = models.SET_NULL, null=True)
    timestamp = models.TimeField()


class Reply(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete = models.CASCADE, null=True)
    content = models.TextField()
    reaction = models.ForeignKey('Reaction', on_delete = models.SET_NULL, null=True)
    

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

    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES, verbose_name='Reaction')


class Repost(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, null=True)
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete = models.SET_NULL, null=True)
    timestamp = models.TimeField()
    reaction = models.ForeignKey('Reaction', on_delete = models.SET_NULL, null=True)
    comments = models.ForeignKey('Comment', on_delete = models.SET_NULL, null=True)
    
class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    post = models.ForeignKey(Post, on_delete = models.SET_NULL, null=True)
    timestamp = models.TimeField()
    

class PromotedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    promotion_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)