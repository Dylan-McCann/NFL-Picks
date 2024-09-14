from django.db import models
from django.conf import settings


class SingletonModel(models.Model):
    """Singleton Django Model"""
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Save object to the database. Removes all other entries if there
        are any.
        """
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        Load object from the database. Failing that, create a new empty
        (default) instance of the object and return it (without saving it
        to the database).
        """
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()

# Create your models here.
class Game(models.Model):
    home_team = models.CharField(max_length=50)
    away_team = models.CharField(max_length=50)
    home_spread = models.CharField(max_length=6)
    ou = models.CharField(max_length=6)
    week = models.IntegerField(default=0)
    home_final = models.IntegerField(default=0)
    away_final = models.IntegerField(default=0)

    class Meta:
        permissions = [
            ("can_update", "Users can update games")
        ]


class Choice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    over = models.CharField(max_length=50)
    under = models.CharField(max_length=50)
    fav = models.CharField(max_length=50)
    dog = models.CharField(max_length=50)
    week = models.IntegerField(default=0)


class Week(SingletonModel):
    curr_week = models.IntegerField(default=0)


class Record(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    overall_wins = models.IntegerField(default=0)
    overall_loss = models.IntegerField(default=0)
    over_win = models.IntegerField(default=0)
    over_loss = models.IntegerField(default=0)
    under_win = models.IntegerField(default=0)
    under_loss = models.IntegerField(default=0)
    fav_loss = models.IntegerField(default=0)
    fav_win = models.IntegerField(default=0)
    dog_loss = models.IntegerField(default=0)
    dog_win = models.IntegerField(default=0)