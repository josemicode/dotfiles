from django.db import models
from django.contrib.auth.models import AbstractUser

#? Nullable fields needed in some cases...

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
    following = models.ManyToManyField("User", related_name="followers")

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
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name="answers", null=True)

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
        return [vote for vote in self.votes if vote.is_like() == positive]

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

class Vote(models.Model):
    is_positive_vote = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    answer = models.ForeignKey(Answer , on_delete=models.CASCADE, related_name="votes")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="votes", null=True)

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