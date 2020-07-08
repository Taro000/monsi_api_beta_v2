from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
import uuid


# Choices list for age, gender, year, state and tag
AGE_CHOICES = tuple([(i, i) for i in range(0, 121)])
GENDER_CHOICES = (('M', '男性'), ('F', '女性'), ('O', 'その他'),)
YEAR_CHOICES = tuple([(k, k) for k in range(0, 100)])
TIME_CHOICES = tuple([(l, l) for l in range(30, 181, 30)])
PROBLEM_CHOICES = (('カラー', 'カラー'),
                   ('縮毛強制', '縮毛強制'),)


User = get_user_model()


class StylistProfile(models.Model):
    stylist = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name='stylist')   # PK
    img = models.ImageField(upload_to='stylist_img')
    phone_number = models.CharField(max_length=32)
    year = models.IntegerField(choices=YEAR_CHOICES)
    salon_name = models.CharField(max_length=32)
    salon_img = models.ImageField(upload_to='salon_img')
    place = models.CharField(max_length=128)
    access = models.CharField(max_length=64)

    def __str__(self):
        return self.stylist.get_full_name()


class Problem(models.Model):
    """
    A stylist is associated with only one tag. Not a number of tags.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # PK
    problem = models.CharField(max_length=32, choices=PROBLEM_CHOICES)

    def __str__(self):
        return self.problem


class Menu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # PK
    stylist = models.ForeignKey('StylistProfile', on_delete=models.CASCADE, related_name='menu')
    menu_name = models.CharField(max_length=64)
    img = models.ImageField(upload_to='menu_img')
    price = models.IntegerField()
    time = models.IntegerField(choices=TIME_CHOICES)
    problem = models.ForeignKey('Problem', on_delete=models.CASCADE)

    def __str__(self):
        return self.menu_name


class CatalogImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # PK
    menu = models.ForeignKey('Menu', on_delete=models.CASCADE, related_name='catalog')
    before_img = models.ImageField(upload_to='before_img')
    after_img = models.ImageField(upload_to='after_img')
    age = models.IntegerField(choices=AGE_CHOICES, blank=True, null=True)
    gender = models.CharField(max_length=8, choices=GENDER_CHOICES)

    def __str__(self):
        return self.menu.menu_name


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
