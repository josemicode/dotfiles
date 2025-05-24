# Django shortcuts
from django.shortcuts import render, get_object_or_404, redirect

# Models
from users.models import Question, SocialRetriever, PopularTodayRetriever, TopicRetriever, NewsRetriever, Topic, Answer, Vote, QuestionRetriever
# —> DUPLICADO más abajo (ver nota)

# HTTP y JSON
from django.http import JsonResponse
from datetime import date


# Autenticación y usuarios
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth import authenticate

# URLs
from django.urls import reverse_lazy

# DRF
from rest_framework.decorators import api_view

# Protección de vistas
from django.views.decorators.http import require_POST

# Content types (para votos genéricos)
from django.contrib.contenttypes.models import ContentType

# Modelos de Django (ORM)
from django.db.models import Count, Q, Max, Exists, OuterRef




from django.utils import timezone
from django.db.models import Avg

@login_required(login_url='login')
def questions_list_view(request):
    recommender = request.GET.get("recommender", "general")

    qs = (
        Question.objects
        .select_related("user")
        .prefetch_related("topics")
        .annotate(
            positive_votes_count=Count(
                'votes', filter=Q(votes__is_positive_vote=True)
            ),
            negative_votes_count=Count(
                'votes', filter=Q(votes__is_positive_vote=False)
            )
        )
    )

    if recommender == "social":
        preguntas = QuestionRetriever.create_social().retrieve_questions(qs, request.user)
    elif recommender == "topic":
        preguntas = QuestionRetriever.create_topics().retrieve_questions(qs, request.user)

    else:
        # Fecha “hoy” según tu zona
        today = timezone.localdate()

        if recommender == "news":
            # Últimas preguntas publicadas hoy
            preguntas = qs.filter(timestamp__date=today).order_by('-timestamp')

        elif recommender == "popular":
            # Filtramos las de hoy...
            today_qs = qs.filter(timestamp__date=today)
            # ...calculamos el promedio de likes de hoy
            avg = today_qs.aggregate(avg_likes=Avg('positive_votes_count'))['avg_likes'] or 0
            # incluimos todas las que superen o igualen el promedio
            preguntas = today_qs.filter(positive_votes_count__gte=avg) \
                                .order_by('-positive_votes_count', '-timestamp')

        else:
            # “general” o fallback
            preguntas = qs.order_by('-timestamp')

    return render(request, "questions_list.html", {
        "preguntas": preguntas,
        "active_recommender": recommender
    })


@api_view(['GET'])
@login_required
def pregunta_detalle_api(request, id):
    pregunta = get_object_or_404(Question, id=id)
    ct = ContentType.objects.get_for_model(Question)

    vote_qs = Vote.objects.filter(
        user=request.user,
        specific_subclass=ct,
        object_id=pregunta.id
    ).order_by('-timestamp')

    vote = vote_qs.first()
    user_vote = None
    if vote:
        user_vote = 'like' if vote.is_positive_vote else 'dislike'

    data = {
        'title': pregunta.title,
        'description': pregunta.description,
        'username': pregunta.user.username,
        'timestamp': pregunta.timestamp.strftime('%d %B %Y %H:%M'),
        'topics': [t.name for t in pregunta.topics.all()],
        'positive_votes': pregunta.positive_votes().count(),
        'negative_votes': pregunta.negative_votes().count(),
        'user_vote': user_vote,
    }
    return JsonResponse(data)

@login_required(login_url='login')
def topics(request):
    topic_order = request.GET.get('topic_order', 'popular')

    if topic_order == 'recientes':
        qs = Topic.objects.order_by('-id')
    elif topic_order == 'alfabetico':
        qs = Topic.objects.order_by('name')
    else:  # popular o por defecto
        qs = Topic.objects.annotate(
            num_questions=Count('questions')
        ).order_by('-num_questions')

    topics = qs
    return render(request, "topics.html", {
        "topics": topics,
        "active_topic_order": topic_order,
    })
 
@login_required(login_url='login')
def responder_pregunta(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        contenido = request.POST.get('description')
        if contenido:
            answer = Answer.objects.create(
                user=request.user,
                question=question,
                description=contenido
            )
            return redirect('responder_pregunta', pk=question.pk)

    ct = ContentType.objects.get_for_model(Answer)
    
    likes_qs = Vote.objects.filter(
        user=request.user,
        specific_subclass=ct,
        object_id=OuterRef('pk'),
        is_positive_vote=True
    )
    
    dislikes_qs = Vote.objects.filter(
        user=request.user,
        specific_subclass=ct,
        object_id=OuterRef('pk'),
        is_positive_vote=False
    )

    respuestas = (
        Answer.objects
        .filter(question=question)
        .annotate(
            positive_votes_count=Count('votes', filter=Q(votes__is_positive_vote=True)),
            negative_votes_count=Count('votes', filter=Q(votes__is_positive_vote=False)),
            user_liked=Exists(likes_qs),
            user_disliked=Exists(dislikes_qs),
        )
    )

    return render(request, 'responder_pregunta.html', {
        'question': question,
        'respuestas': respuestas,
        'active_tab': 'responder',
    })
    
@login_required
def update_username(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu nombre de usuario ha sido actualizado.")
            return redirect('home')
    else:
        form = UserChangeForm(instance=request.user)
    
    return render(request, 'update_username.html', {'form': form})


class CustomLogoutView(LogoutView):
    next_page = '/home/'  # Redirigir al home después de cerrar sesión
    

class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True


class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')
    
    
    
def test_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            return render(request, 'success.html', {'user': user})
        else:
            return render(request, 'error.html', {'error': 'Usuario o contraseña incorrectos'})
    return render(request, 'login_test.html')





def home_view(request):
    user    = request.user
    mode    = request.GET.get("recommender", "general")
    
    
    qs = (
        Question.objects
        .select_related('user')
        .prefetch_related('topics')
        .annotate(
            positive_votes_count=Count('votes', filter=Q(votes__is_positive_vote=True)),
            negative_votes_count=Count('votes', filter=Q(votes__is_positive_vote=False))
        )
    )

 
    if mode in ("news", "reciente"):
        preguntas = qs.order_by('-timestamp')
    elif mode == "popular":
        preguntas = qs.order_by('-positive_votes_count', '-timestamp')
    elif mode == "social":
        preguntas = SocialRetriever().retrieve_questions(qs, user)
    elif mode in ("topic", "relevante"):
        preguntas = TopicRetriever().retrieve_questions(qs, user)
    else:
        preguntas = list(qs)
    
   
    preguntas = preguntas[:4]

    
    topic_order = request.GET.get("topic_order", "popular")
    if topic_order == "recientes":
        topics = (
            Topic.objects
            .annotate(last_question_time=Max('questions__timestamp'))
            .order_by('-last_question_time')
        )
    if topic_order == "alfabetico":
        topics = Topic.objects.order_by('name')
    else:
        topics = (
            Topic.objects
            .annotate(num_questions=Count('questions'))
            .order_by('-num_questions')
        )

   
    topics = topics[:4]

    return render(request, "home.html", {
        "preguntas":           preguntas,
        "topics":              topics,
        "active_recommender":  mode,
        "active_topic_order":  topic_order,
    })
    


def topic_detail(request, id):
    topic = get_object_or_404(Topic, id=id)
    num_preguntas = topic.questions.count()
    return JsonResponse({
        "id": topic.id,
        "name": topic.name,
        "description": topic.description,
        "num_preguntas": num_preguntas,
    })
    
    
@login_required
@require_POST
def vote_pregunta_api(request, id):
    user = request.user
    question = get_object_or_404(Question, pk=id)

    vote_type = request.POST.get('vote')
    ct = ContentType.objects.get_for_model(Question)

    existing = Vote.objects.filter(
        user=user,
        specific_subclass=ct,
        object_id=question.id
    ).order_by('-timestamp').first()

    if existing and (
        (vote_type == 'like'    and existing.is_positive_vote) or
        (vote_type == 'dislike' and not existing.is_positive_vote)
    ):
      
        existing.delete()
    else:
      
        if existing:
            existing.is_positive_vote = (vote_type == 'like')
            existing.save()
        else:
            Vote.objects.create(
                user=user,
                specific_subclass=ct,
                object_id=question.id,
                is_positive_vote=(vote_type == 'like')
            )

   
    positive = question.votes.filter(is_positive_vote=True).count()
    negative = question.votes.filter(is_positive_vote=False).count()

    return JsonResponse({
        'positive_votes': positive,
        'negative_votes': negative,
    })
    
    
@login_required
@require_POST
def vote_respuesta_api(request, id):
    
    answer    = get_object_or_404(Answer, pk=id)
    vote_type = request.POST.get('vote')  # 'like' o 'dislike'
    ct        = ContentType.objects.get_for_model(Answer)

   
    existing = Vote.objects.filter(
        user=request.user,
        specific_subclass=ct,
        object_id=answer.id
    ).first()

    if existing:
        if (vote_type == 'like'    and existing.is_positive_vote) or \
           (vote_type == 'dislike' and not existing.is_positive_vote):
            existing.delete()
        else:
            existing.is_positive_vote = (vote_type == 'like')
            existing.save()
    else:
        Vote.objects.create(
            user=request.user,
            specific_subclass=ct,
            object_id=answer.id,
            is_positive_vote=(vote_type == 'like')
        )

    positive = answer.votes.filter(is_positive_vote=True).count()
    negative = answer.votes.filter(is_positive_vote=False).count()

    return JsonResponse({
        'positive_votes': positive,
        'negative_votes': negative,
    })
    
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q, Exists, OuterRef
from users.models import Answer, Vote

@login_required(login_url='login')
def answers_list_view(request):
    # 1. Averiguamos el ContentType de Answer
    ct = ContentType.objects.get_for_model(Answer)

    # 2. Preparamos dos subqueries para Exists()
    likes_qs = Vote.objects.filter(
        user=request.user,
        specific_subclass=ct,
        object_id=OuterRef('pk'),
        is_positive_vote=True
    )
    dislikes_qs = Vote.objects.filter(
        user=request.user,
        specific_subclass=ct,
        object_id=OuterRef('pk'),
        is_positive_vote=False
    )

    # 3. Annotate sobre Answer
    answers = (
        Answer.objects
        .annotate(
            positive_votes_count=Count('votes', filter=Q(votes__is_positive_vote=True)),
            negative_votes_count=Count('votes', filter=Q(votes__is_positive_vote=False)),
            user_liked=Exists(likes_qs),
            user_disliked=Exists(dislikes_qs),
        )
        .order_by('-timestamp')
    )

    return render(request, 'answers_list.html', {
        'answers': answers
    })
