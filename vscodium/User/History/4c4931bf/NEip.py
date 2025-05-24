from rest_framework import routers, serializers, viewsets
from todomanager.models import Board
from api.serializers import BoardSerializer
from todomanager.tasks import send_notifications

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
    serializer_class = BoardSerializer

    def perform_create(self, serializer):
        print("Creating a new board...")
        instance = serializer.save()
        send_notifications.delay(instance.id)
        print("Board created successfully!")
