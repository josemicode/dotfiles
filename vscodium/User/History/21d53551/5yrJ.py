from django.shortcuts import render
import random
from .models import User, Notification
from django.contrib.auth.decorators import login_required


def users_view(request):
    users = User.objects.all()
    context = {"users": users}
    return render(request, "users_list.html", context)

def user_detail_view(request, user_id):
    user = User.objects.get(id=user_id)
    context = {"user": user}
    return render(request, "user_detail.html", context)

def user_list(request):
    users = User.objects.all()
    return render(request, 'users_list.html', {'users': users})

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('timestamp')
    context = {
        'notifications': notifications,
    }

    #FIXME: no html yet, so don't run lol
    return render(request, 'notifications.html', context)
