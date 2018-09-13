from django.db import models
from datetime import*
from django.urls import*
from django.contrib.auth.models import Permission, User
from django.db.models.signals import post_save

from Sloth import settings
# Create your models here.


class Project(models.Model):
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    pro_title = models.CharField(max_length=30)
    pro_desc = models.TextField(max_length=300)
    pro_pic = models.FileField(upload_to='pro_pics', default='pro_pics/Dummy_projekt.png', blank=True)
    pro_complete = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('pro', kwargs={'pk':self.pk})

    def __str__(self):
        return self.pro_title


class Task(models.Model):

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    task_title = models.CharField(max_length=50)
    task_explain = models.CharField(max_length=1500)
    task_imp = models.IntegerField(default=0)
    task_dead = models.DateTimeField(default=datetime.now, blank=True)
    task_eff = models.FloatField(default=1.0)
    complete = models.BooleanField(default=False)
    task_start = models.DateTimeField(default=datetime.now, blank=True)
    id_field = models.CharField(max_length=8, default="id_field")
    task_end = models.DateTimeField(default=datetime.now, blank=True)
    shifted = models.BooleanField(default=False)
    shift_time = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.task_title


class ChecklistItem(models.Model):
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    Item_title = models.CharField(max_length=30)
    checked = models.BooleanField(default=False)

    def __str__(self):
        return self.Item_title


class UserMsg(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    textmsg = models.CharField(max_length=300)
    sender = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    post_time = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return self.textmsg


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.CharField(default='Deutschland', blank=True, max_length=11)
    age = models.DateField(default=datetime.now, blank=True, null=True)
    icon = models.ImageField(upload_to='profile_image', blank=True, null=True)
    agree = models.BooleanField(default=False)
    cust_icon = models.BooleanField(default=False)
    agree2 = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])


post_save.connect(create_profile, sender=User)


class Subscriber(models.Model):
    email = models.EmailField(max_length=70, blank=True)

    def __str__(self):
        return self.email


class UserFeed(models.Model):
    post_time = models.DateTimeField(default=datetime.now())
    user = models.OneToOneField(User, on_delete=models.SET_DEFAULT, default=1)
    promotion = models.IntegerField(default=0)
    feature = models.CharField(max_length=500)
    control = models.IntegerField(default=0)
    like = models.CharField(max_length=500)

    def __str__(self):
        return self.user.username


class FirstFeed(models.Model):
    post_time = models.DateTimeField(default=datetime.now)
    how = models.CharField(max_length=21, default='Angesprochener Tester')
    impress = models.IntegerField(default=0)
    impact = models.IntegerField(default=0)
    opinion = models.CharField(max_length=300)
    mail = models.EmailField(default='admin@sloth.de')

    def __str__(self):
        return self.how


class LearnLike(models.Model):
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    like = models.NullBooleanField(blank=True, null=True, default=None)

    def __str__(self):
        return self.user.username
