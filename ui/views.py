from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q 
import datetime, pytz

from ui.models import Webrequest, Webtitle, Websearch, Webimage, Webnetflix, Host

def index(request):
            
    hosts = Host.objects.all()
    
    timeframes = (('All time',0),('Today',1),('Yesterday',2),('This Week',3))
    
    # host_id of 0 shows all computers on network
    if request.GET.get('host',''):
        host_id = int(request.GET.get('host'))
    else:
        host_id = 0
    
    if host_id >= 0 and host_id < 25:
        # If it is 0-25, set it on session
        request.session['filteredhost'] = host_id
                
    if 'filteredhost' in request.session and int(request.session.get('filteredhost')) > 0 and int(request.session.get('filteredhost')) < 25:
        # Filter all lists down to only requests that came from single host_id
        filteredhost = int(request.session['filteredhost'])
        
        unsorted_dupes = Webrequest.objects.filter(Q(istitle=True) | Q(images__isnull=False)).filter(host_id=filteredhost)
        latest_search_list = Websearch.objects.filter(webrequest__host_id=filteredhost).order_by('id')
        latest_skintone_image_list = Webimage.objects.filter(height__gte=150).filter(width__gte=150).filter(tone__gte=35).filter(webrequest__host_id=filteredhost).order_by('id')
        latest_netflix_list = Webnetflix.objects.filter(webrequest__host_id=filteredhost).order_by('id')
    else:
        # No filter on hosts
        filteredhost = 0

        # convert list of dupes to a set to remove dupes, then return a list
        unsorted_dupes = Webrequest.objects.filter(Q(istitle=True) | Q(images__isnull=False))    
        latest_search_list = Websearch.objects.order_by('webrequest__t')
        latest_skintone_image_list = Webimage.objects.filter(height__gte=150).filter(width__gte=150).filter(tone__gte=35).order_by('webrequest__t')
        latest_netflix_list = Webnetflix.objects.order_by('webrequest__t')
    
    # timeframe of 0 shows all time
    if request.GET.get('timeframe',''):
        timeframe = int(request.GET.get('timeframe'))
    elif 'timeframe' in request.session:
        timeframe = int(request.session.get('timeframe'))
    else:
        # If its not in the request and not in the session, default to today only
        timeframe = 1
        
    
    if timeframe >= 0 and timeframe <= 3:
        # If it is 0-3, set it on session
        request.session['timeframe'] = timeframe
        
    if 'timeframe' in request.session and int(request.session.get('timeframe')) >= 1 and int(request.session.get('timeframe')) <= 3:
        # If 1, filter to today only.  If 2, filter to yesterday only, If 3, filter to this week.  If 0, no filter.
        timeframe = int(request.session['timeframe'])
        local_tz = pytz.timezone('America/Los_Angeles')
        
        if timeframe is 1:
            gte = datetime.datetime.now(tz=local_tz).replace(hour=0,minute=0,second=0)   
            lte = datetime.datetime.now(tz=local_tz)         
        if timeframe is 2:
            lte = datetime.datetime.now(tz=local_tz).replace(hour=0,minute=0,second=0)           
            gte = lte - datetime.timedelta(days=1)
        if timeframe is 3:
            today = datetime.datetime.now(tz=local_tz).replace(hour=0,minute=0,second=0)
            numberofdaystosubtract = today.weekday() + 1
            gte = today - datetime.timedelta(days=numberofdaystosubtract)
            lte = datetime.datetime.now(tz=local_tz)         
            
        unsorted_dupes = unsorted_dupes.filter(t__gte=gte).filter(t__lte=lte)
        latest_search_list = latest_search_list.filter(webrequest__t__gte=gte).filter(webrequest__t__lte=lte)
        latest_netflix_list = latest_netflix_list.filter(webrequest__t__gte=gte).filter(webrequest__t__lte=lte)
        latest_skintone_image_list = latest_skintone_image_list.filter(webrequest__t__gte=gte).filter(webrequest__t__lte=lte)
        
    # eliminate dupes by converting to set, converting back to list, then sorting (might be better way out there..)
    unsorted_no_dupes = list(set(unsorted_dupes))
    istitle_or_hasimages_requests = sorted(unsorted_no_dupes, key=lambda x:x.t, reverse=True)
    
    # take the slice as last operation (so we can filter)
    latest_search_list = latest_search_list.reverse()[:50]
    latest_skintone_image_list = latest_skintone_image_list.reverse()[:200]
    
    context = {'timeframes': timeframes, 'startingtimecode': timeframe, 'filteredhost': filteredhost, 'istitle_or_hasimages_requests': istitle_or_hasimages_requests, 'hosts': hosts, 'latest_search_list': latest_search_list, 'latest_netflix_list': latest_netflix_list, 'latest_skintone_image_list': latest_skintone_image_list }
    return render(request, 'ui/index.html', context)

def webtitledetail(request, title_id):
    title = get_object_or_404(Webtitle, pk=title_id)
    return render(request, 'ui/webtitledetail.html', {'title': title})

def webimagedetail(request, image_id):
    image = get_object_or_404(Webimage, pk=image_id)
    return render(request, 'ui/webimagedetail.html', {'image': image})
