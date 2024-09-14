from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import PasswordInput, TextInput
from poolapp.models import Game,Week


class CreateUserForm(UserCreationForm):
  class Meta:
    model = User
    fields = ['username', 'password1', 'password2']


class LoginUserForm(AuthenticationForm):
  username = forms.CharField(widget=TextInput())
  password = forms.CharField(widget=PasswordInput())


class ChoiceForm(forms.Form):
  over = forms.ModelChoiceField(queryset=None, label='Over')
  under = forms.ModelChoiceField(queryset=None, label='Under')
  dog = forms.ModelChoiceField(queryset=None, label='Dogs')
  fav = forms.ModelChoiceField(queryset=None, label='Favs')
  def __init__(self, *args, **kwargs):
    super(ChoiceForm,self).__init__(*args, **kwargs)
    week = Week.load().curr_week
    self.fields['over'].choices = self.getOverList(week)
    self.fields['under'].choices = self.getUnderList(week)
    self.fields['dog'].choices = self.getDogList(week)
    self.fields['fav'].choices = self.getFavList(week)

  def getOverList(self, week):
    choiceList = []
    for game in Game.objects.filter(week=week):
      if str(game.home_final) == "0" and str(game.away_final) == "0":
        data = []
        data.append(game.home_team)
        data.append(game.ou)
        read = str(game.home_team) + " vs. " + str(game.away_team) + " over: " + str(game.ou)[1:]
        choice = (data, read)
        choiceList.append(choice)
    return choiceList

  def getUnderList(self,week):
    choiceList = []
    for game in Game.objects.filter(week=week):
      if str(game.home_final) == "0" and str(game.away_final) == "0":
        data = []
        data.append(game.home_team)
        data.append(game.ou)
        read = str(game.home_team) + " vs. " + str(game.away_team) + " under: " + str(game.ou)[1:]
        choice = (data, read)
        choiceList.append(choice)
    return choiceList
  
  def getFavList(self,week):
    choiceList = []
    for game in Game.objects.filter(week=week):
      if str(game.home_final) == "0" and str(game.away_final) == "0":
        if game.home_spread[0] == "-":
          data = []
          data.append(game.home_team)
          data.append(game.home_spread)
          read = str(game.home_team) + " " + str(game.home_spread)
        else:
          data = []
          data.append(game.away_team)
          data.append("-" + game.home_spread[1:])
          read = str(game.away_team) + " -" + game.home_spread[1:]
        choice = (data, read)
        choiceList.append(choice)
    return choiceList
  
  def getDogList(self,week):
    choiceList = []
    for game in Game.objects.filter(week=week):
      if str(game.home_final) == "0" and str(game.away_final) == "0":
        if game.home_spread[0] == "+":
          data = []
          data.append(game.home_team)
          data.append(game.home_spread)
          read = str(game.home_team) + " " + str(game.home_spread)
        else:
          data = []
          data.append(game.away_team)
          data.append("+" + game.home_spread[1:])
          read = str(game.away_team) + " +" + game.home_spread[1:]
        choice = (data, read)
        choiceList.append(choice)
    return choiceList

class UpdateGamesForm(forms.Form):
  week = forms.IntegerField()

  
