from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, 'campus/home.html')

def about(request):
    return render(request, 'campus/about.html')