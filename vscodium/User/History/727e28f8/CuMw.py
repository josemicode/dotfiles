from django.shortcuts import render
from users.models import Question

def home(request):
    return render(request, 'home.html')

def socials(request):
    questions = Question.objects.all()
    context = {"questions": questions}
    return render(request, 'recommended.html')