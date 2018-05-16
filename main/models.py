# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import django.contrib.auth.models as auth_models


# Create your models here.



class AuthorMod(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    birth_date = models.DateField(max_length=30)

    def __unicode__(self):
        return '%s %s' % (self.name, self.surname)


class Book(models.Model):
    title = models.CharField(max_length=50)
    lc_classification = models.CharField(max_length=50)
    authors = models.ManyToManyField(AuthorMod, related_name="books")

    def __unicode__(self):
        return '%s %s' % (self.title, self.lc_classification)
