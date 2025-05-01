from django.shortcuts import render, get_object_or_404, redirect
from users.models import Question, SocialRetriever, PopularTodayRetriever, TopicRetriever, NewsRetriever, Topic, Answer
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from django.http import JsonResponse



# def home(request):
#     preguntas = Question.objects.select_related('user').all()[:4]
#     topics = Topic.objects.all()[:4]
#     return render(request, 'home.html', {'preguntas': preguntas, 'topics':topics})

def socials(request):
    user = request.user
    questions = Question.objects.all()
    retrieved_questions = SocialRetriever().retrieve_questions(questions, user)
    context = {"questions": retrieved_questions}
    return render(request, 'recommended.html', context)

@login_required(login_url='login')
def questions_list_view(request):
    preguntas = Question.objects.select_related("user").prefetch_related("topics").all().order_by("-timestamp")
    return render(request, "questions_list.html", {"preguntas": preguntas})


def pregunta_detalle_api(request, id):
    pregunta = get_object_or_404(Question, id=id)
    data = {
        'title': pregunta.title,
        'description': pregunta.description,
        'username': pregunta.user.username,
        'timestamp': pregunta.timestamp.strftime('%d %B %Y %H:%M'),
        'topics': [t.name for t in pregunta.topics.all()]
    }
    return JsonResponse(data)

@login_required(login_url='login')
def topics(request):
    topics = Topic.objects.all()
    return render(request, "topics.html", {"topics": topics})

@login_required(login_url='login')
def responder_pregunta(request, pk):
    question = get_object_or_404(Question, pk=pk)
    respuestas = Answer.objects.filter(question=question)

    if request.method == 'POST':
        contenido = request.POST.get('description')
        if contenido:
            Answer.objects.create(
                user=request.user,
                question=question,
                description=contenido
            )
            return redirect('responder_pregunta', pk=question.pk)

    return render(request, 'responder_pregunta.html', {
        'question': question,
        'respuestas': respuestas,
    })
    
@login_required
def update_username(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu nombre de usuario ha sido actualizado.")
            return redirect('home')  # O la página a la que quieras redirigir después
    else:
        form = UserChangeForm(instance=request.user)
    
    return render(request, 'update_username.html', {'form': form})


class CustomLogoutView(LogoutView):
    next_page = '/home/'  # Redirigir al home después de cerrar sesión
    

class CustomLoginView(LoginView):
    template_name = 'login.html'  # Ruta a tu template
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
    # --- Recommender ---
    user = request.user
    recommender = request.GET.get("recommender", "general")
    preguntas_base = Question.objects.all()
    print(recommender)

    if recommender == "popular":
        #? preguntas = Question.objects.order_by('-num_likes')[:4]
        preguntas = PopularTodayRetriever().retrieve_questions(preguntas_base, user)
    elif recommender == "reciente":
        #? preguntas = Question.objects.order_by('-created_at')[:4]
        preguntas = NewsRetriever().retrieve_questions(preguntas_base, user)
    elif recommender == "relevante":
        preguntas = TopicRetriever().retrieve_questions(preguntas_base, user)
    elif recommender == "social":
        preguntas = SocialRetriever().retrieve_questions(preguntas_base, user)
    else:  # social o default
        #? preguntas = Question.objects.order_by('?')[:4]  # o tu lógica "social"
        preguntas = preguntas_base

    # --- Topics ---
    topic_order = request.GET.get("topic_order", "popular")

    """ if topic_order == "recientes":
        topics = Topic.objects.order_by('-created_at')[:4]
    elif topic_order == "alfabetico":
        topics = Topic.objects.order_by('name')[:4]
    else:  # popular o default
        topics = Topic.objects.order_by('-num_questions')[:4]  # o lo que uses como "popular" """

    context = {
        "preguntas": preguntas,
        "topics": topics,
        "active_recommender": recommender,
        "active_topic_order": topic_order,
    }
    return render(request, "home.html", context)


def topic_detail(request, id):
    topic = get_object_or_404(Topic, id=id)
    return JsonResponse({
        "id": topic.id,
        "name": topic.name,
        "description": topic.description,
    })