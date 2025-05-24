from rest_framework import routers, serializers, viewsets
from .models import Question
from api.serializers import QuestionSerializer
from .tasks import send_notifications

# ViewSets define the view behavior.
# class BoardViewSet(viewsets.ModelViewSet):
#     queryset = Board.objects.all()
#     serializer_class = BoardSerializer

#     def perform_create(self, serializer):
#         print("Creating a new board...")
#         instance = serializer.save()
#         send_notifications.delay(instance.id)
#         print("Board created successfully!")

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def perform_create(self, serializer):
        print("Pu lishing a question..")
        instance = serializer.save()
        send_notifications.delay(instance.id)
        print("NEW Question!")
