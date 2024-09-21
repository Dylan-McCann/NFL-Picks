from django.shortcuts import render,redirect
from . forms import CreateUserForm,LoginUserForm,ChoiceForm,UpdateGamesForm
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_protect
from urllib.request import  urlopen
from bs4 import BeautifulSoup
from . models import Game,Choice,Week,Record

@login_required()
def index(request):
	week = Week.load().curr_week
	this_weeks_games = Game.objects.filter(week=week)
	context = {"this_weeks_games":this_weeks_games}
	return render(request, 'poolapp/index.html', context=context)

def standings(request):
	standings = Record.objects.order_by("overall_wins")
	context = {"standings":standings}
	return render(request, 'poolapp/standings.html', context=context)


def picks(request):
	week= Week.load().curr_week
	picks = Choice.objects.get(user=request.user, week=week)
	context = {"picks":picks}
	return render(request, 'poolapp/picks.html', context=context)	
		

@csrf_protect
def register(request):
	form = CreateUserForm()
	if request.method == "POST":
		form = CreateUserForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect("login")
	context = {'registerform':form}
	return render(request, 'poolapp/register.html', context=context)
		

def userlogout(request):
	logout(request)
	return redirect("")


@login_required()
@csrf_protect
def dashboard(request):
	form = ChoiceForm()
	if request.method == 'POST':
		form = ChoiceForm(request, request.POST)
		week = Week.load().curr_week
		if Choice.objects.filter(user=request.user).filter(week=week):
			Choice.objects.filter(week=week).filter(user=request.user).update(over=request.POST.get('over'), under=request.POST.get('under'), fav=request.POST.get('fav'), dog=request.POST.get('dog'))
		else:
			c = Choice.objects.create(user=request.user,over=request.POST.get('over'),week=week, under=request.POST.get('under'), fav=request.POST.get('fav'), dog=request.POST.get('dog'))
			c.save()
		return redirect('')
	context = {'choiceform': form}
	return render(request, 'poolapp/dashboard.html', context=context)



@user_passes_test(lambda u: u.is_superuser)
@csrf_protect
def updategames(request):
	form = UpdateGamesForm()
	if request.method =='POST':
		form = UpdateGamesForm(request, request.POST)
		week = request.POST.get('week')
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
		return redirect("dashboard")
	context = {'updategamesform':form}
	return render(request, 'poolapp/updategames.html', context=context)

def updateRecords(request):
	if request.method == 'GET':
		week = Week.load().curr_week
		url = "https://www.cbssports.com/nfl/scoreboard/2024/regular/"
		page = urlopen(url + str(week))
		html = page.read().decode("utf-8")
		soup = BeautifulSoup(html, "html.parser")
		tables = soup.find_all('table')
		for table in tables:
			score = table.find_all('td', attrs={'class':'total'})
			teams = table.find_all("a",attrs={'class':'team-name-link'})
			awayteam = teams[0].get_text()
			hometeam = teams[1].get_text()
			away_score = score[0].get_text()
			home_score = score[1].get_text()
			Game.objects.filter(week=week,home_team=hometeam,away_team=awayteam).update(away_final=away_score, home_final=home_score)
		picks = Choice.objects.filter(week=str(week))
		for pick in picks:
			over_pick_list = str(pick.over).strip('][').split(', ')
			over_pick_hometeam = over_pick_list[0].strip('\'')
			over_pick_total = over_pick_list[1].strip('\'o')
			under_pick_list = str(pick.under).strip('][').split(', ')
			under_pick_hometeam = under_pick_list[0].strip('\'')
			under_pick_total = under_pick_list[1].strip('\'o')
			over_game = Game.objects.filter(week=week,home_team=over_pick_hometeam)[0]
			under_game = Game.objects.filter(week=week,home_team=under_pick_hometeam)[0]
			if not Record.objects.filter(user=pick.user):
				w = Record.objects.create(user=pick.user)
				w.save()
			wl = Record.objects.get(user=pick.user)
			if float((int(over_game.home_final) + int(over_game.away_final))) < float(over_pick_total):
				wl.overall_loss = wl.overall_loss+1
				wl.over_loss = wl.over_loss+1
			elif abs(float(int(over_game.home_final) + int(over_game.away_final)) - float(over_pick_total)) < 0.1:
				wl.overall_push = wl.overall_push+1
				wl.over_push = wl.over_push+1
			else:
				wl.overall_wins = wl.overall_wins+1
				wl.over_win = wl.over_win+1
			if float((int(under_game.home_final) + int(under_game.away_final))) < float(under_pick_total):
				wl.overall_wins = wl.overall_wins+1
				wl.under_win = wl.under_win+1
			elif abs(float(int(under_game.home_final) + int(under_game.away_final)) - float(under_pick_total)) < 0.1:
				wl.overall_push = wl.overall_push+1
				wl.under_push = wl.under_push+1
			else:
				wl.overall_loss = wl.overall_loss+1
				wl.under_loss = wl.under_loss+1
			wl.save()
		for pick in picks:
			fav_pick_list = str(pick.fav).strip('][').split(', ')
			fav_pick_team = fav_pick_list[0].strip('\'')
			fav_pick_spread = fav_pick_list[1].strip('\'-')
			dog_pick_list = str(pick.dog).strip('][').split(', ')
			dog_pick_team = dog_pick_list[0].strip('\'')
			dog_pick_spread = dog_pick_list[1].strip('\'+')
			fav_game = Game.objects.filter(week=week,home_team=fav_pick_team)
			if not fav_game:
				fav_game = Game.objects.filter(week=week,away_team=fav_pick_team)[0]
				fav_score = fav_game.away_final
				not_fav_score = fav_game.home_final
			else:
				fav_game = fav_game[0]
				fav_score = fav_game.home_final
				not_fav_score = fav_game.away_final
			wl = Record.objects.get(user=pick.user)
			if (float(fav_score) - float(fav_pick_spread)) > not_fav_score:
				wl.overall_wins = wl.overall_wins+1
				wl.fav_win = wl.fav_win+1
			elif abs((float(fav_score) - float(fav_pick_spread)) - not_fav_score) < 0.1:
				wl.overall_push = wl.overall_push+1
				wl.fav_push = wl.fav_push+1
			else:
				wl.overall_loss = wl.overall_loss+1
				wl.fav_loss = wl.fav_loss+1

			dog_game = Game.objects.filter(week=week,home_team=dog_pick_team)
			if not dog_game:
				dog_game = Game.objects.filter(week=week,away_team=dog_pick_team)[0]
				dog_score = dog_game.away_final
				not_dog_score = dog_game.home_final
			else:
				dog_game = dog_game[0]
				dog_score = dog_game.home_final
				not_dog_score = dog_game.away_final
			if (float(dog_score) + float(dog_pick_spread)) > not_dog_score:
				wl.overall_wins = wl.overall_wins+1
				wl.dog_win = wl.dog_win+1
			elif abs((float(dog_score) +float(dog_pick_spread)) - not_dog_score) < 0.1:
				wl.overall_push = wl.overall_push+1
				wl.dog_push = wl.dog_push+1
			else:
				wl.overall_loss = wl.overall_loss+1
				wl.dog_loss = wl.dog_loss+1 
			wl.save()
	return redirect('updategames')

def standings(request):
	standings = Record.objects.all()
	context = {"standings":standings}
	return render(request, 'poolapp/standings.html', context=context)