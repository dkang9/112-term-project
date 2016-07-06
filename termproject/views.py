from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponseRedirect

from backend.models import *
import requests

#Classes to change UI 
class Index(View):
    def get(self, request):
        return render(request, 'index.html')
        
class Result(View):
    def get(self, request):
        return render(request, 'result.html')
        
class Landing(View):
    def get(self, request):
        return render(request, 'landing.html')
        
class TakeInfo(View):
    def post(self, request):
    	answers = str(request.POST.get("q1")) + "," + str(request.POST.get("q2"))+ "," +str(request.POST.get("q3"))+ "," +str(request.POST.get("q4"))+ "," +str(request.POST.get("q5"))
        (name,region,lane,partner) = (request.POST.get("name"),request.POST.get("region"),request.POST.get("lane"),request.POST.get("partner"))
        kda = findKda(name.lower(),region)
        originalName = str(name)
        (rank,winRate) = getRank(str(name).lower(),str(region).lower())
        newForm = Form(name=str(name), region=str(region).lower(), lane=str(lane).lower(), partner=str(partner).lower(), pref=answers, rank=rank, mostPlayed=findMostPlayed(str(region).lower(),str(name).lower()),winRate=winRate,kda=kda)
        newForm.save()
        forms = Form.objects.all()
        nameList = createNameDict(forms)
        rankBuddies = findClosestRank(newForm,nameList)
        (match, matchPercent) = findMatch(newForm,rankBuddies)
        print(match,matchPercent)
        context = {"matchData" : {"match":match, "matchPercent":matchPercent}}
        return render(request, 'result.html',context)

def createNameDict(forms): #creates a list of all dictionaries of summoners mapping a list of region, lane, pref and rank to a key that's the summoner name. 
    list = []
    for form in forms:
        dict = {}
        (name,region,lane,partner,pref,rank,mostPlayed,winRate,kda) = (str(form.name),str(form.region),str(form.lane),str(form.partner),str(form.pref),str(form.rank),str(form.mostPlayed),str(form.winRate),str(form.kda))
        dict["player"] = {"name":name,"region":region,"lane":lane,"partner":partner,"pref":pref,"rank":rank,"mostPlayed":mostPlayed,"mostPlayedLower":mostPlayed.lower(),"winRate":winRate,"kda":kda}
        list.append(dict)
    return list

#Helper Functions for Classes

def contextConverter(list):
	return "I lob swang"
	
def makeList(string):
	result = []
	for character in string.split(","):
		result.append(character)
	return result
	
def percentTruncate(value):
	result = float(round(value*10))
	result = result/10
	return result
	
def percentWholeTruncate(value): #doesn't leave any decimals in the percent
	result = float(round(value))
	return result

#Matching Functions

def findClosestRank(newForm, nameList): #finds a list of players that are within 1 division of the player. (also checks for correct region) (also checks for correct lane preference)
	#assigned each tier as follows: bronze = 1, silver = 2, gold = 3, platinum = 4, diamond = 5, masters = 6, challenger = 7
	newPlayerTier = tierConvert(newForm.rank) #converts a rank (say PLATINUM 5) to a tier number as given above 
	rankBuddies = []
	for name in nameList: 
		nameTier = tierConvert(name["player"]["rank"].lower())
		#checking if tiers and region are compatible
		if (nameTier-1 == newPlayerTier or nameTier == newPlayerTier or nameTier+1 == newPlayerTier) and name["player"]["name"] != newForm.name and name["player"]["region"] == newForm.region and name["player"]["lane"] == newForm.partner: 
			rankBuddies += [name]
	return rankBuddies
	
def findMatch(newForm, rankBuddies): #takes rankbuddies and gives me the best match 
	newPrefs = makeList(str(newForm.pref))
	print(newPrefs)
	bestMatch = None 
	bestMatchCount = 0
	for buddy in rankBuddies:
		count = 0
		buddyPref = makeList(buddy["player"]["pref"])
		for i in range(5): #changes value of scores based on how important question is
			if i == 0 and (newPrefs[i] == buddyPref[i] or (newPrefs[i]=="both" or (buddyPref[i]=="both"))):
				count += 4
			if i == 1 and (newPrefs[i] == buddyPref[i] or (newPrefs[i]=="both" or (buddyPref[i]=="both"))):
				count += 2
			if i == 2 and (newPrefs[i] == buddyPref[i] or (newPrefs[i]=="both" or (buddyPref[i]=="both"))):
				count += 5
			if i == 3 and (newPrefs[i] == buddyPref[i] or (newPrefs[i]=="both" or (buddyPref[i]=="both"))):
				count += 2
			if i == 4 and (newPrefs[i] == buddyPref[i] or (newPrefs[i]=="both" or (buddyPref[i]=="both"))):
				count += 2
		if count > bestMatchCount:
			bestMatch = buddy
			bestMatchCount = count 
		print(bestMatchCount)
	print(bestMatchCount)
	matchPercent = int(float(bestMatchCount)/float(15)*100)
	return (bestMatch,matchPercent)
    	
    
#Riot API Functions

def getSummonerData(region, summonerName, apiKey): #returns a dict of some info, such as summoner name, level, and id 
	summonerName = summonerName.lower()
	link = "https://" + region + ".api.pvp.net/api/lol/" + region + "/v1.4/summoner/by-name/" + summonerName + "?api_key=" + apiKey
	result = requests.get(link)
	return result.json()

def getRankedStats(region, id, apiKey): #gives more stats based on summoner id like tier, rank, name of divison, whether you're on a hot streak etc. 
	link = "https://" + region + ".api.pvp.net/api/lol/" + region + "/v2.5/league/by-summoner/" + str(id) + "/entry?api_key=" + apiKey
	result = requests.get(link)
	return result.json()

def getTier(name,region):
    print(name,region)
    apiKey = "9916d3a9-903e-49bc-a0be-840be3097f9f"
    summonerData = getSummonerData(region,name,apiKey)
    summonerId = str(summonerData[name]["id"])
    rankedStats = getRankedStats(region, summonerId, apiKey)
    tier = rankedStats[summonerId][0]["tier"]
    division = rankedStats[summonerId][0]["entries"][0]["division"]
    return ("%s %s" % (tier,division)) 

def getRank(name,region):
    apiKey = "9916d3a9-903e-49bc-a0be-840be3097f9f"
    summonerData = getSummonerData(region,name,apiKey)
    summonerId = str(summonerData[name]["id"])
    rankedStats = getRankedStats(region, summonerId, apiKey)
    tier = rankedStats[summonerId][0]["tier"]
    division = rankedStats[summonerId][0]["entries"][0]["division"]
    wins = float(rankedStats[summonerId][0]["entries"][0]["wins"])
    losses = float(rankedStats[summonerId][0]["entries"][0]["losses"])
    ratio = percentTruncate((wins/(wins+losses)) *100)
    return ("%s %s" % (tier,division),ratio) 
    
def tierConvert(rank): #converts rank into numbered tier as defined above
	if rank.lower().startswith("bronze"):
		return 1
	if rank.lower().startswith("silver"):
		return 2
	if rank.lower().startswith("gold"):
		return 3
	if rank.lower().startswith("platinum"):
		return 4
	if rank.lower().startswith("diamond"):
		return 5
	if rank.lower().startswith("master"):
		return 6
	if rank.lower().startswith("challenger"):
		return 7

def showStats(region,summonerName,apiKey): # takes both functions above and returns the rank of the summoner inputted
	summonerName = summonerName.lower()
	summonerData = getSummonerData(region,summonerName,apiKey)
	summonerId= str(summonerData[summonerName]["id"])
	rankedStats = getRankedStats(region, summonerId, apiKey)
	tier = rankedStats[summonerId][0]["tier"]
	division = rankedStats[summonerId][0]["entries"][0]["division"]
	return ("%s is currently %s %s" % (summonerName, tier, division))

def findMostPlayed(region,summonerName): #find the 3 most played 
	apiKey = "9916d3a9-903e-49bc-a0be-840be3097f9f"
	summonerData = getSummonerData(region,summonerName,apiKey)
	summonerId= str(summonerData[summonerName]["id"])
	championIds = []
	champions = []
	finalString =""
	link = "https://na.api.pvp.net/championmastery/location/%s1/player/%s/topchampions?count=1&api_key=%s" % (region,summonerId,apiKey)
	result = requests.get(link).json() #list of dictionaries of the top champion
	for dictionary in result: 
		championIds += [dictionary["championId"]]

	for id in championIds:  #gives me champ names 
		championLink = "https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion/%s?api_key=%s" % (id,apiKey)
		championResult = requests.get(championLink).json()
		champ = (championResult["name"])
		champions += [champ]

	for champion in champions: #just building up the return string 
		if champions.index(champion) == 0:
			finalString += champion
		else: finalString += "," + champion 
	return (finalString)

def findKda(name,region): 
	apiKey = "9916d3a9-903e-49bc-a0be-840be3097f9f"
	summonerData = getSummonerData(region,name,apiKey)
	summonerId= str(summonerData[name.lower()]["id"])
	link = "https://na.api.pvp.net/api/lol/%s/v1.3/stats/by-summoner/%s/ranked?season=SEASON2016&api_key=9916d3a9-903e-49bc-a0be-840be3097f9f" % (region,summonerId)
	result = requests.get(link).json()
	print(result)
	averageKills = percentTruncate(float(result["champions"][-1]["stats"]["totalChampionKills"]) / float(result["champions"][-1]["stats"]["totalSessionsPlayed"]))
	averageDeaths = percentTruncate(float(result["champions"][-1]["stats"]["totalDeathsPerSession"]) / float(result["champions"][-1]["stats"]["totalSessionsPlayed"]))
	averageAssists = percentTruncate(float(result["champions"][-1]["stats"]["totalAssists"]) / float(result["champions"][-1]["stats"]["totalSessionsPlayed"]))
	kda = "%s/%s/%s" % (averageKills,averageDeaths,averageAssists)
	return kda


	
