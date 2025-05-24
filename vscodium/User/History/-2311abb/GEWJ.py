from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from abc import ABC, abstractmethod
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Count, Q

from datetime import datetime




#! Modularize

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    #...
    #user_name = models.CharField(max_length=15, null=True)
    #password = models.CharField(max_length=20, null=True)
    #* votes is referenced
    #* questions is referenced
    #* answers is referenced
    topics_of_interest = models.ManyToManyField("Topic", related_name="users")
    following = models.ManyToManyField("User", related_name="followers", blank=True) #? No effect...

    def add_topic(self, a_topic):
        self.topics_of_interest.add(a_topic)

    def get_votes(self):
        return self.votes.all()

    def add_question(self, a_question):
        self.questions.append(a_question)

    def get_username(self):
        return self.username

    def get_questions(self):
        return self.questions.all()

    def follow(self, a_user):
        self.following.add(a_user)

    def stop_follow(self, a_user):
        self.following.remove(a_user)

    def get_answers(self):
        return self.answers.all()

    def get_following(self):
        return self.following.all()

    def add_vote(self, a_vote):
        self.votes.add(a_vote)

    def get_password(self):
        return self.password

    def add_answer(self, an_answer):
        self.answers.add(an_answer)

    def get_topics_of_interest(self):
        return self.topics_of_interest.all()

    def set_password(self, password):
        self.password = password

    def set_username(self, username):
        self.username = username

    def calculate_score(self):
        question_score = sum(10 for q in self.questions.all() if len(q.positive_votes()) > len(q.negative_votes()))
        answer_score = sum(20 for a in self.answers.all() if len(a.positive_votes()) > len(a.negative_votes()))
        return question_score + answer_score

class Votable(models.Model):
    
    votes = GenericRelation(
        'Vote',
        content_type_field='specific_subclass',
        object_id_field='object_id',
        related_query_name='votable'
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def get_timestamp(self):
        return self.timestamp

    def _filter_votes(self, is_positive):
        #return [vote for vote in self.votes if vote.is_like() == positive]
        return self.votes.filter(is_positive_vote=is_positive)
    
    def positive_votes(self):
        return self._filter_votes(True)
    
    def negative_votes(self):
        return self._filter_votes(False)

    """ def add_vote(self, a_vote):
        if any(vote.user == a_vote.user for vote in self.votes.all()):
            raise ValueError("Este usuario ya ha votado")
        self.votes.append(a_vote) """
    
    def add_vote(self, a_vote):
        if self.votes.filter(pk=a_vote.pk).exists():
            raise ValueError("Ya ha votado el usuario.")
        self.votes.add(a_vote)
    
    def get_votes(self):
        return self.votes.all()

class Answer(Votable):
    #timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    #? Autoset...
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answers")
    #* votes is referenced
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name="answers")

    #* check -> API
    apto = models.BooleanField(null=True, default=None)

    def get_question(self):
        return self.question
		
    def get_user(self):
        return self.user

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description
    
    def __str__(self):
        return f"In response to <<{self.question.get_title()}>> by {self.user.get_username()}"

class Topic(models.Model):
    name = models.CharField(max_length=75)
    description = models.TextField()
    #* questions is referenced

    def add_question(self, a_question):
        self.questions.add(a_question)

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_questions(self):
        return self.questions.all()
    
    def __str__(self):
        return f"{self.get_name()}"

class Question(Votable):
    #timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    #* answers is referenced
    #* votes is referenced
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")
    topics = models.ManyToManyField(Topic, related_name="questions")

    #* check -> API
    apto = models.BooleanField(null=True, default=None)

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def get_topics(self):
        return self.topics.all()

    def get_title(self):
        return self.title
    
    def set_title(self, a_title):
        self.title = a_title

    def get_user(self):
        return self.user
    
    def add_topic(self, a_topic):
        if self.topics.filter(pk=a_topic.pk).exists():
            raise ValueError("El tópico ya está agregado.")
        self.topics.add(a_topic)

    def add_answer(self, answer):
        self.answers.add(answer)

    def get_best_answer(self):
        if self.answers.count() == 0:
            return None
        
        return sorted(self.answers.all(), key=lambda a: len(a.positive_votes()) - len(a.negative_votes()), reverse=True)[0]

    def __str__(self):
        return f"{self.get_title()}"

#! Refactoring Votable
class Vote(models.Model):
    is_positive_vote = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = (
            ("user", "specific_subclass", "object_id"),
        )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")

    """ answer = models.ForeignKey(Answer , on_delete=models.CASCADE, related_name="votes", null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="votes", null=True, blank=True) """

    specific_subclass = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="votes")
    object_id = models.PositiveIntegerField()
    votable = GenericForeignKey('specific_subclass', 'object_id')

    #...
    def is_like(self):
        return self.is_positive_vote
    
    def get_user(self):
        return self.user

    def like(self):
        self.is_positive_vote = True

    def dislike(self):
        self.is_positive_vote = False
    
    def __str__(self):
        return f"By {self.user.get_username()}"

class QuestionRetrievalStrategy(ABC):
    @abstractmethod
    def retrieve_questions(self, questions, a_user):
        pass
class SocialRetriever(QuestionRetrievalStrategy):
    def retrieve_questions(self, questions_qs, a_user):
        # 1) Sacamos los IDs de los usuarios a los que sigo
        following_ids = a_user.following.values_list('id', flat=True)
        # 2) Filtramos sólo las preguntas de esos usuarios
        qs = questions_qs.filter(user__id__in=following_ids)
        # 3) Ordenamos primero por número de votos positivos, luego por fecha
        return qs.annotate(
            positive_votes_count=Count('votes', filter=Q(votes__is_positive_vote=True))
        ).order_by('-positive_votes_count', '-timestamp')

class TopicRetriever(QuestionRetrievalStrategy):
    def retrieve_questions(self, questions, a_user):
        topics_questions = []
        for topic in a_user.get_topics_of_interest():
            topics_questions.extend(topic.questions.all())
        sorted_q = sorted(topics_questions, key=lambda q: len(q.positive_votes()))
        q_ret = sorted_q[-min(100, len(sorted_q)):]
        return [q for q in q_ret if q.user != a_user]

from django.utils import timezone

class NewsRetriever(QuestionRetrievalStrategy):
    def retrieve_questions(self, questions, a_user):
        today = timezone.localdate()
        # Filtramos usando ORM cuando sea posible:
        if hasattr(questions, 'filter'):
            qs = questions.filter(timestamp__date=today)
            return [q for q in qs if q.user != a_user]
        # Fallback en listas:
        return [q for q in questions if timezone.localtime(q.timestamp).date() == today and q.user != a_user]

class PopularTodayRetriever(QuestionRetrievalStrategy):
    def retrieve_questions(self, questions, a_user):
        today = timezone.localdate()
        # Si es QuerySet
        if hasattr(questions, 'annotate'):
            # Primero, anota los likes
            qs = questions.filter(timestamp__date=today)
            # Calcula promedio de likes
            avg = qs.aggregate(avg_likes=Avg('positive_votes_count'))['avg_likes'] or 0
            return list(qs.filter(positive_votes_count__gte=avg).order_by('-positive_votes_count', '-timestamp'))
        # Si es lista pura
        today_qs = [q for q in questions if timezone.localtime(q.timestamp).date() == today]
        if not today_qs:
            return []
        avg = sum(q.positive_votes().count() for q in today_qs) / len(today_qs)
        return sorted(
          [q for q in today_qs if q.positive_votes().count() >= avg and q.user != a_user],
          key=lambda q: q.positive_votes().count(),
          reverse=True
        )


class QuestionRetriever: #!

    @classmethod
    def create_social(cls):
        return SocialRetriever()

    @classmethod
    def create_topics(cls):
        return TopicRetriever()

    @classmethod
    def create_news(cls):
        return NewsRetriever()

    @classmethod
    def create_popular_today(cls):
        return PopularTodayRetriever()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    #? BooleanField -> read?

    #? timestamp.strftime('%Y-%m-%d %H:%M')
    def __str__(self):
        return f"{self.description}"