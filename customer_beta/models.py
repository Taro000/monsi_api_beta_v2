from django.db import models
from django.contrib.auth import get_user_model
from stylist_beta import models as stylist_models
import uuid
from django.contrib.postgres.fields import ranges
from django.core.exceptions import ValidationError
import datetime


# Choices list for age, gender and rate
AGE_CHOICES = tuple([(i, i) for i in range(0, 121)])
GENDER_CHOICES = (('M', '男性'), ('F', '女性'), ('O', 'その他'),)
RATE_CHOICES = tuple([(0.5*j, 0.5*j) for j in range(11)])


User = get_user_model()


class CustomerProfile(models.Model):
    customer = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name='customer')    # PK
    img = models.ImageField(upload_to='customer_img')
    age = models.IntegerField(choices=AGE_CHOICES, blank=True, null=True)
    gender = models.CharField(max_length=3, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=32)

    def __str__(self):
        return self.customer.get_full_name()


class Timeslots(models.Model):
    """
    Model for preventing double-booking and allowing for easy temporal queries.
    Uses Postgresql's range datatype via DateTimeRangeField.
    Basis for other scheduling-related models, which inherit id.
    TODO: Find way to add SQL for EXCLUDE constraint
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # PK
    time = ranges.DateTimeRangeField()
    stylist = models.ForeignKey(stylist_models.StylistProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.stylist.stylist.get_full_name()}-{self.time}'


class ReserveAndHistory(Timeslots):
    """
    {2}Need a function to post a State data(Reserved) in customer_v1.models automatically
    if a timetable of a day is filled in reserves
    """
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    menu = models.ForeignKey(stylist_models.Menu, on_delete=models.CASCADE)
    rating = models.FloatField(choices=RATE_CHOICES, blank=True, null=True)

    def __str__(self):
        return f'''{self.customer}-{self.menu}
-{self.rating if self.rating is not None else "Unrated"}{super().__str__}'''
