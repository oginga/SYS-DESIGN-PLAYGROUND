from pastebinclone.models import Paste
from pastebinclone.forms import PasteForm
from django.shortcuts import render
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.contrib import messages

import re
from functools import reduce
from datetime import datetime


BASE_62_ALPHABET=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def base_62_encode(num,base=62):
    digitz=[]
    while num > 0:
        remainder=num%base
        digitz.append(remainder)
        num=int(num/base)
    digitz.reverse()
    
    shortened=""
    for digit in digitz:
        shortened+=BASE_62_ALPHABET[digit]
    return shortened


def base_62_decode(suffix,base=62):
    # get the index of each xter
    indices=[ BASE_62_ALPHABET.index(character) for character in suffix]
    paste_db_id= reduce(lambda a,b: a+(62 ** indices.index(b)+b),indices)
    print(f"Paste db id: {paste_db_id}")
    return paste_db_id

def index(request):
    if request.method == 'POST':
        paste_form=PasteForm(request.POST)
        print(f"POST::{request.POST}")
        # Creating a new paste, assumes all pastes are unique
        newPaste=Paste()
        newPaste.content=request.POST['content']
        # Convert date to datetime
        rgxPat=r"^[0-3]?[0-9]/[0-3]?[0-9]/(?:[0-9]{2})?[0-9]{2}$"
        if re.match(rgxPat,request.POST['expiry']):
            dt=datetime.strptime(request.POST['expiry'], '%d/%m/%Y')
            # Check if date is in the past
            if dt > datetime.today():
                newPaste.expiry=dt
                newPaste.save()

                # Get id of last insert
                shortlink_suffix=base_62_encode(newPaste.id)
                print(f"SHORTLINK: {shortlink_suffix} PID: {newPaste.id}")
                shortlink=f"http://127.0.0.1:8000/{shortlink_suffix}"
                newPaste.shortlink=shortlink

                messages.success(request,('Content saved successfully'))
                return TemplateResponse(request,'index.html',{'shortlink':shortlink})
            else:
                messages.warning(request,('Please provide a date not in the past'))
                return TemplateResponse(request,'index.html',{'form':paste_form})        
        else:
            messages.warning(request,('Please provide a valid date format as specified by the placeholder'))
            return TemplateResponse(request,'index.html',{'form':paste_form})    
    else:
        paste_form=PasteForm()
        return TemplateResponse(request,'index.html',{'form':paste_form})

def content(request,*args,**kwargs):
    if request.method == 'GET':
        suffix=kwargs.get('suffix',None)
        if suffix:
            paste_id=base_62_decode(suffix)
            paste=Paste.objects.get(id=paste_id)
            if paste:
                if paste.is_expired:
                    return TemplateResponse(request,'content.html',{'content':paste.content})
                else:
                    return TemplateResponse(request,'content.html',{'content':"Sorry,Content has expired!"})
            else:
                return TemplateResponse(request,'content.html',{'content':"No content available!"})


