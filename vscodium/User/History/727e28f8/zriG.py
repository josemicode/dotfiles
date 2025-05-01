from django.shortcuts import render
from users.models import Question, SocialRetriever

def home(request):
    return render(request, 'home.html')

def socials(request):
    user = request.user
    questions = Question.objects.all()
    retrieved_questions = SocialRetriever().retrieve_questions(questions, user)
    context = {"questions": retrieved_questions}
    return render(request, 'recommended.html', context)