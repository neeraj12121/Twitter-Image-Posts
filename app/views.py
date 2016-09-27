import calendar
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from app.models import Album
import tweepy


c_key = ''
c_secret = ''
token_key = ''
token_secret = ''


auth = tweepy.OAuthHandler(c_key,c_secret)
auth.set_access_token(token_key,token_secret)

api = tweepy.API(auth)


@login_required(login_url="login/")
def home(request):
    results = api.search(q="#carnival")

    list_url=[]
    retweet=[]
    retweet_dict={}

    for result in results:
        r = str(result)
        position = r.find('media_url_https')
        t = r[position + 19:].find('\'')
        if (position >= 0):
            url = r[position + 19:position + 19 + t]
            list_url.append(str(url))

        retweet_position = r.find('retweet_count')
        t = r[retweet_position:].find(',')
        if (retweet_position >= 0):
            count = r[retweet_position + 16:retweet_position + t]
            retweet.append(int(count))

    size = len(list_url)

    for i in range(0, size):
        retweet_dict[list_url[i]] = retweet[i]

    url_list_in_database = Album.objects.all().filter(user=request.user).values('image_url')

    temp = []
    for url in url_list_in_database:
        temp.append(str(url['image_url']))

    url_list_in_database = temp

    new_urls = list(set(list_url) - set(url_list_in_database))

    for url in new_urls:
        album = Album(image_url=url, user=request.user, retweet_count=retweet_dict[url])
        album.save()

    temp = Album.objects.all().filter(user=request.user).values('image_url', 'time_added', 'retweet_count')

    url_list = {}

    for entry in temp:
        dt = str(entry['time_added'])[0:10]
        dt = calendar.month_name[int(dt[5:7])] + " " + dt[8:10] + ", " + dt[0:4]
        url_list[str(entry['image_url'])] = (dt, str(entry['retweet_count']))

    print(url_list)
    total_entries_in_database = len(url_list)

    return render(request, 'home.html', {'url_list': url_list})