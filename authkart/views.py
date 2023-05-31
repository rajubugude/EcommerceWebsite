from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages

from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token

  

def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return render(request, 'login.html')
        
        # if len(username)>20:
        #     messages.error(request, "Username must be under 20 charcters!!")
        #     return redirect('home')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return render(request, 'signup.html')
        
        # if not username.isalnum():
        #     messages.error(request, "Username must be Alpha-Numeric!!")
        #     return redirect('home')
        
        myuser = User.objects.create_user(email, email, pass1)
        # # myuser.is_active = False
        myuser.is_active = False

        messages.success(request, "!! Please check your email to confirm your email address in order to activate your account.")
        
   
        # # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Activate Your Account !! "
        message2 = render_to_string('activate.html',{
            
            'name': myuser.email,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
        email_subject,
        message2,
        settings.EMAIL_HOST_USER,
        [myuser.email],
        )
        email.fail_silently = True
        email.send()
        myuser.save()
        
        return redirect('/auth/login/')
        
        
    return render(request,"signup.html")   


def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('/auth/login/')
    else:
        return render(request, 'activatefail.html')
    
    

def handlelogin(request):
    if request.method == 'POST':
        username = request.POST['email']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            messages.success(request, "Logged In Sucessfully!!")
            return redirect('/')
        else:
            messages.error(request, "Invalid Credentials!!")
            return redirect('/auth/login')
    
    return render(request, "login.html")



def handlelogout(request):
    logout(request)
    messages.info(request,"Logout Success")
    return redirect('/auth/login')
