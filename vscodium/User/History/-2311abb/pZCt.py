from django.db import models
from django.contrib.auth.models import AbstractUser
from abc import ABC, abstractmethod

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
    following = models.ManyToManyField("User", related_name="followers", null=True, blank=True) #? No effect...

    def add_topic(self, a_topic):
        self.topics_of_interest.append(a_topic)

    def get_votes(self):
        return self.votes

    def add_question(self, a_question):
        self.questions.append(a_question)

    def get_username(self):
        return self.username

    def get_questions(self):
        return self.questions

    def follow(self, a_user):
        self.following.append(a_user)

    def stop_follow(self, a_user):
        self.following.remove(a_user)

    def get_answers(self):
        return self.answers

    def get_following(self):
        return self.following

    def add_vote(self, a_vote):
        self.votes.append(a_vote)

    def get_password(self):
        return self.password

    def add_answer(self, an_answer):
        self.answers.append(an_answer) 

    def get_topics_of_interest(self):
        return self.topics_of_interest

    def set_password(self, password):
        self.password = password

    def set_username(self, username):
        self.username = username

    def calculate_score(self):
        question_score = sum(10 for q in self.questions if len(q.positive_votes()) > len(q.negative_votes()))
        answer_score = sum(20 for a in self.answers if len(a.positive_votes()) > len(a.negative_votes()))
        return question_score + answer_score

class Answer(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    #? Autoset...
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answers")
    #* votes is referenced
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name="answers")

    def _filter_votes(self, positive):
        return [vote for vote in self.votes if vote.is_like() == positive]

    def positive_votes(self):
        return self._filter_votes(True)
    
    def negative_votes(self):
        return self._filter_votes(False)

    def get_question(self):
        return self.question
		
    def get_user(self):
        return self.user

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description
	
    def get_timestamp(self):
        return self.timestamp

    def add_vote(self, a_vote):
        if any(vote.user == a_vote.user for vote in self.votes):
            raise ValueError("Este usuario ya ha votado")
        self.votes.append(a_vote)

    def get_votes(self):
        return self.votes
    
    def __str__(self):
        return f"In response to <<{self.question.get_title()}>> by {self.user.get_username()}"

class Topic(models.Model):
    name = models.CharField(max_length=75)
    description = models.TextField()
    #* questions is referenced

    def add_question(self, a_question):
        self.questions.append(a_question)

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_questions(self):
        return self.questions
    
    def __str__(self):
        return f"{self.get_name()}"

class Question(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    #* answers is referenced
    #* votes is referenced
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")
    topics = models.ManyToManyField(Topic, related_name="questions")

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def _filter_votes(self, positive: bool):
        return [vote for vote in self.votes.all() if vote.is_like() == positive]

    def positive_votes(self):
        return self._filter_votes(True)
    
    def negative_votes(self):
        return self._filter_votes(False)

    def get_topics(self):
        return self.topics

    def get_title(self):
        return self.title
    
    def set_title(self, a_title):
        self.title = a_title

    def get_user(self):
        return self.user

    def get_timestamp(self):
        return self.timestamp

    def get_votes(self):
        return self.votes

    def add_vote(self, a_vote):
        if any(vote.user == a_vote.user for vote in self.votes): 
            raise ValueError("Este usuario ya ha votado")
        self.votes.append(a_vote)

    def add_topic(self, a_topic):
        if a_topic in self.topics:
            raise ValueError("El topico ya esta agregado.")
        self.topics.append(a_topic)
        a_topic.add_question(self)

    def add_answer(self, answer):
        self.answers.append(answer)

    def get_best_answer(self):
        if not self.answers:
            return None
        
        return sorted(self.answers, key=lambda a: len(a.positive_votes()) - len(a.negative_votes()), reverse=True)[0]

    def __str__(self):
        return f"{self.get_title()}"

#! Refactoring Votable
class Vote(models.Model):
    is_positive_vote = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    answer = models.ForeignKey(Answer , on_delete=models.CASCADE, related_name="votes", null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="votes", null=True, blank=True)

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
    def retrieve_questions(self, questions, a_user):
        following_questions = []
        for follow in a_user.following.all():
            following_questions.extend(follow.questions.all())
        sorted_q = sorted(following_questions, key=lambda q: len(q.positive_votes().count()))
        q_ret = sorted_q[-min(100, len(sorted_q)):]
        return [q for q in q_ret if q.user != a_user]

class TopicRetriever(QuestionRetrievalStrategy):
    def retrieve_questions(self, questions, a_user):
        topics_questions = []
        for topic in a_user.get_topics_of_interest():
            topics_questions.extend(topic.questions)
        sorted_q = sorted(topics_questions, key=lambda q: len(q.positive_votes()))
        q_ret = sorted_q[-min(100, len(sorted_q)):]
        return [q for q in q_ret if q.user != a_user]

class NewsRetriever(QuestionRetrievalStrategy):
    def retrieve_questions(self, questions, a_user):
        news_questions = [q for q in questions if q.timestamp.date() == datetime.today().date()]
        sorted_q = sorted(news_questions, key=lambda q: len(q.positive_votes()))
        q_ret = sorted_q[-min(100, len(sorted_q)):]
        return [q for q in q_ret if q.user != a_user]

class PopularTodayRetriever(QuestionRetrievalStrategy):
    def retrieve_questions(self, questions, a_user):
        today_questions = [q for q in questions if q.timestamp.date() == datetime.today().date()]
        if today_questions:
            average_votes = sum(len(q.positive_votes()) for q in today_questions) / len(today_questions)
            popular_questions = [q for q in today_questions if len(q.positive_votes()) > average_votes]
            sorted_q = sorted(popular_questions, key=lambda q: len(q.positive_votes()))
            q_ret = sorted_q[-min(100, len(sorted_q)):]
        else:
            q_ret = []
        return [q for q in q_ret if q.user != a_user]

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

#? How to test...
class CuOOra:
    def __init__(self):
        self.questions = []

    def add_question(self, question):
        self.questions.append(question)

    def get_questions_by_type(self, type_, user):
        retriever_methods = {
            "social": QuestionRetriever.create_social,
            "topic": QuestionRetriever.create_topics,
            "news": QuestionRetriever.create_news,
            "popular": QuestionRetriever.create_popular_today,
        }
        if type_ not in retriever_methods:
            raise ValueError("Tipo de pregunta no válido")
        retriever = retriever_methods[type_]()
        return retriever.retrieve_questions(self.questions, user)

    def get_social_questions_for_user(self, user):
        return self.get_questions_by_type("social", user)

    def get_topic_questions_for_user(self, user):
        return self.get_questions_by_type("topic", user)

    def get_news_questions_for_user(self, user):
        return self.get_questions_by_type("news", user)

    def get_popular_questions_for_user(self, user):
        return self.get_questions_by_type("popular", user)