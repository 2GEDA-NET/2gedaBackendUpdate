from rest_framework import serializers
from .models import PastQuestion, University


# class GeneralPastQuestionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PastQuestion
#         fields = ['past_question_file']



class UniversityNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['name']

class PastQuestionSerializer(serializers.ModelSerializer):
    university = UniversityNameSerializer()
    class Meta:
        model = PastQuestion
        fields = ['university', 'past_question_file']

