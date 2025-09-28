from django.shortcuts import render
from app.forms import ContactForm

# Create your views here.
def index(reqest):
    con = ContactForm()
    return render(reqest,'index.html',{'form':con})