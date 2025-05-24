from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from home.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', home_view, name='home'),
    path('', home_view, name='home'),
    path('users/', include('users.urls'), name='users'),
    #path('socials/', socials, name='socials'),
    path("questions/", questions_list_view, name = "questions_list"),
    path("topics/", topics, name = "topics"),
    path('api/topic/<int:id>/', topic_detail, name='topic_api'),
    path('api/pregunta/<int:id>/', pregunta_detalle_api, name='pregunta_api'),
    path('pregunta/<int:pk>/responder/', responder_pregunta, name='responder_pregunta'),
    path("logout/", CustomLogoutView.as_view(next_page='home'), name="logout"),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('test-login/', test_login, name='test_login'),
    path('api/topic/<int:id>/', topic_detail, name='topic-detail'),
    path('api/pregunta/<int:id>/vote/', vote_pregunta_api, name='api_pregunta_vote'),
    path('api/respuesta/<int:id>/vote/', vote_respuesta_api, name='api_respuesta_vote'),
    path('answers/', answers_list_view, name='answers_list'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
