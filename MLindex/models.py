from django.db import models
from django import forms

class Member(models.Model):
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.firstname} | {self.lastname} | {self.email} | {self.password}'
                

