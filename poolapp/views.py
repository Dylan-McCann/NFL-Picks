from django.shortcuts import render,redirect
from . forms import CreateUserForm,LoginUserForm,ChoiceForm,UpdateGamesForm
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required, user_passes_test
from urllib.request import  urlopen
from bs4 import BeautifulSoup
from . models import Game,Choice,Week

@login_required(login_url="userlogin")
def index(request):
	week = Week.load().curr_week
	this_weeks_games = Game.objects.filter(week=week)
	context = {"this_weeks_games":this_weeks_games}
	return render(request, 'poolapp/index.html', context=context)


def register(request):
	form = CreateUserForm()
	if request.method == "POST":
		form = CreateUserForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect("userlogin")
	context = {'registerform':form}
	return render(request, 'poolapp/register.html', context=context)
		

def userlogin(request):
	form = LoginUserForm()
	if request.method == 'POST':
		form = LoginUserForm(request, data=request.POST)
		if form.is_valid():
			username = request.POST.get('username')
			password = request.POST.get('password')
			user = authenticate(request, username=username,password=password)
			if user is not None:
				login(request, user)
				return redirect("")
	context = {'loginuserform':form}
	return render(request, 'poolapp/userlogin.html', context=context)


def userlogout(request):
	logout(request)
	return redirect("")


@login_required(login_url="userlogin")
def dashboard(request):
	form = ChoiceForm()
	if request.method == 'POST':
		form = ChoiceForm(request, request.POST)
		week = Week.load().curr_week
		'''same_game = bool(Game.objects.filter(week=week).filter(home_team=request.POST.get('dog')).filter(away_team=request.POST.get('fav')) or Game.objects.filter(week=week).filter(away_team=request.POST.get('dog')).filter(home_team=request.POST.get('fav')))
		if request.POST.get('over')[0] == request.POST.get('under')[0] or same_game:
			context = {'choiceform': form}
			return redirect(request, 'poolapp/dashboard.html', context=context)'''
		if Choice.objects.filter(user=request.user).filter(week=week):
			Choice.objects.filter(week=week).filter(user=request.user).update(over=request.POST.get('over'), under=request.POST.get('under'), fav=request.POST.get('fav'), dog=request.POST.get('dog'))
		else:
			c = Choice.objects.create(user=request.user,over=request.POST.get('over'),week=week, under=request.POST.get('under'), fav=request.POST.get('fav'), dog=request.POST.get('dog'))
			c.save()
		return redirect('')
	context = {'choiceform': form}
	return render(request, 'poolapp/dashboard.html', context=context)



@user_passes_test(lambda u: u.is_superuser)
def updategames(request):
	form = UpdateGamesForm()
	if request.method =='POST':
		form = UpdateGamesForm(request, request.POST)
		week =  request.POST.get('week')
		temp = Week.load()
		temp.curr_week = week
		temp.save()
		url = "https://www.cbssports.com/nfl/scoreboard/2024/regular/"
		page = urlopen(url + week)
		html = page.read().decode("utf-8")
		soup = BeautifulSoup(html, "html.parser")
		tables = soup.find_all('table')
		for table in tables:
			ouf = table.find('td', attrs={'class':'in-progress-odds in-progress-odds-away'})
			if ouf is not None:
				ou = ouf.get_text()
				spreadf = table.find('td', attrs={'class':'in-progress-odds in-progress-odds-home'})
				spread = spreadf.get_text()
				teams = table.find_all('td', attrs={'class':'team team--nfl'})
				away = teams[0].text[:-3]
				home = teams[1].text[:-3]
				if not Game.objects.filter(week=week).filter(home_team=home).filter(away_team=away):
					g = Game.objects.create(home_team=home, away_team=away, home_spread=spread, ou=ou, week=week)
					g.save()
				else:
					Game.objects.filter(week=week).filter(home_team=home).filter(away_team=away).update(ou=ou,home_spread=spread)

			else:
				score = table.find_all('td', attrs={'class':'total'})
				teams = table.find_all("a",attrs={'class':'team-name-link'})
				awayteam = teams[0].get_text()
				hometeam = teams[1].get_text()
				away_score = score[0].get_text()
				home_score = score[1].get_text()
				Game.objects.filter(week=week,home_team=hometeam,away_team=awayteam).update(away_final=away_score, home_final=home_score)
		return redirect("dashboard")
	context = {'updategamesform':form}
	return render(request, 'poolapp/updategames.html', context=context)

