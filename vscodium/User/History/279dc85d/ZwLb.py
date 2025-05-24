from django.urls import path, include
from rest_framework import routers
from api.views import QuestionViewSet
# Routers provide an easy way of automatically determining the URL conf.

router = routers.DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='questions')

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]