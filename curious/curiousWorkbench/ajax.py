import json
from django.http import Http404, HttpResponse
from urlparse import urlparse, parse_qs
import requests
urlBase ="http://localhost:8080/contacts-app-0.0.1-SNAPSHOT/"
def more_todo(request):
    if request.is_ajax():
        url= urlBase + "/contactses"

        response =  requests.get(url)
        if (response.ok):
            jsonData= json.loads(response.content)
        todo_items = ['Mow Lawn', 'Buy Groceries',]
        data = json.dumps(jsonData["_embedded"]["contactses"])
        return HttpResponse(data, content_type='application/json')
    else:
        raise Http404


def searchContacts(request):
    if request.is_ajax():

        searchParam= str(request.GET.get('q'))
        url= urlBase + "/rest/search/name/"+searchParam + "*"
        print(url)
        response =  requests.get(url)
        if (response.ok):
            jsonData= json.loads(response.content)
        data = json.dumps(jsonData)
        return HttpResponse(data, content_type='application/json')
    else:
        raise Http404
def details(request):
    if request.is_ajax():

        searchParam= str(request.GET.get('i'))
        url= urlBase + "/rest/search/name/"+searchParam
        print(url)
        response =  requests.get(url)
        if (response.ok):
            jsonData= json.loads(response.content)
        data = json.dumps(jsonData)
        return HttpResponse(data, content_type='application/json')
    else:
        raise Http404
def add_todo(request):
    if request.is_ajax() and request.POST:
        data = {'message': "%s added" % request.POST.get('item')}
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        raise Http404
