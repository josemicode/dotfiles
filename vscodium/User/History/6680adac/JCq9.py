from rest_framework import serializers
from rest_framework.permissions import AllowAny
from user.models import Question, Answer

# class BoardSerializer(serializers.HyperlinkedModelSerializer):
#     permission_classes = [AllowAny]
#     class Meta:
#         model = Board
#         fields = ['id', 'title']

class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    permission_classes = [AllowAny]
    class Meta:
        model = Question
        fields = ['id', 'title', 'description']

#...