"""
Definition of models.
"""

from django.db import models
from django.db.models.fields import CharField

# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    subject = models.CharField(max_length=200, default='None')

class Choice(models.Model):
    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    correct = models.BooleanField(default=False)

class User(models.Model):
    email = models.CharField(max_length=200)
    nombre = models.CharField(max_length=200)

class Ranking(models.Model):
    nombre = models.CharField(max_length=200,primary_key=True)
    score = models.IntegerField(default=1)