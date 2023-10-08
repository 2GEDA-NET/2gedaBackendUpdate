from django.db import models

# Create your models here.

class University(models.Model):
    name = models.CharField(max_length=40, null=False, blank=False, unique=True)
    # university_question = models.ForeignKey(PastQuestion, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class PastQuestion(models.Model):
    past_question_file = models.FileField(upload_to='media/past_question')
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    # class Meta:
    
    #     def __str__(self):
    #         return {self.past_question_f}




    
