from django.db import models
from user.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime
# Create your models here.

earning_medium = (
    ("login", "login"),
    ("post_creation", "post_creation"),
    ("comments", "comments"),
    ("stick", "stick"),
    ("likes", "likes"),
    ("stickers", "stickers"),
    ("time_rewards", "time_rewards"),
    ("commerce", "commerce"),
    ("start_livestream", "start_livestream"),
    ("engage_livestream", "engage_livestream"),
    ("buy_tickets", "buy_tickets"),
    ("sell_tickets","sell_tickets"),
    ("stereo", "stereo"),
)



class Reward(models.Model):
    user = models.ForeignKey(User, verbose_name=_("Each User"), on_delete=models.CASCADE)
    bonus = models.IntegerField(verbose_name=_("current bonus"), default=1)
    prev_bonus = models.IntegerField(verbose_name=_("previous bonus"), null=True, blank=True)
    medium = models.CharField(_("medium of earning"), max_length=50, choices=earning_medium, default="login")
    time_stamp = models.DateTimeField(default=timezone.now)

    def prev_records(self):
        user = Reward.objects.filter(user=self.user).last()
        last_login = user.time_stamp
        last_medium = user.medium
        if self.medium=="login":
            if last_medium == "login" and  str(last_login) == str(datetime.today()):
                return True
        return False
  

    def save(self, *args, **kwargs) -> None:

        if self.prev_records and self.medium == "login":
            pass

        super(Reward, self).save(*args, **kwargs) 


class Claim_Reward_Model(models.Model):
    user = models.ForeignKey(User, verbose_name=_("each_user"), on_delete=models.CASCADE)
    claims = models.IntegerField(_("total claims"), default=0)
    total_claims = models.IntegerField(_("total claims"), default=0)
    medium = models.CharField(_("medium"), max_length=256)
    timestamp = models.DateTimeField(_("date created"), default=timezone.now)

    def check_bonus(self):
        user = Claim_Reward_Model.objects.filter(user=self.user)
        if not user.exists():
            return 0
        current_claim = user.last().total_claims
        return int(current_claim)
    
    def save(self, *args, **kwargs):
        if self.claims:
            self.total_claims = self.check_bonus() + self.claims
            Reward.objects.filter(user=self.user, medium=self.medium).delete()

        super(Claim_Reward_Model, self).save(*args, **kwargs)

    def cashout_reward(self):
        user = Claim_Reward_Model.objects.filter(user=self.user).last()
        if user.total_claims > 500:
            Claim_Reward_Model.objects.filter(user=self.user).delete()



