from django.shortcuts import render
from django.http import HttpResponse
from . import flashsub
import os

def main_page(request):
    if request.method == "POST":
        path = request.POST.get('path')
        user = request.POST.get('user')
        passwd = request.POST.get('password')
        proxy = request.POST.get('proxy')
        if os.path.isdir(path):
            flashsub.run(path,proxy,user,passwd)
            return HttpResponse("Done")
        else:       
            return HttpResponse("Enter correct path")
    return render(request,"flashsubs_app/main.html")
