from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from django.core.mail import EmailMessage
import smtplib, ssl
from django.views import View

from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import token_generator
# Create your views here.

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            messages.add_message(request, messages.SUCCESS, 'Oturum acildi.')
            return redirect('index')
        else:
            messages.add_message(request, messages.ERROR, 'Hatali kullanici adi ya da parola')
            return redirect('login')

    else:
        return render(request, 'user/login.html')


def register(request):
    if request.method == 'POST':

        # get form values

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repassword = request.POST['repassword']

        if password == repassword:
            # Username
            if User.objects.filter(username=username).exists():
                messages.add_message(request, messages.WARNING, 'Bu kullanici adi daha once alinmis')
                return redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.add_message(request, messages.WARNING, 'Bu email daha once alinmis')
                    return redirect('register')
                else:
                    # her sey guzel
                    user = User.objects.create_user(username=username, password=password, email=email)
                    user.is_active = False
                    user.save()

                    # path to view
                    # - getting domain we are on
                    # - relative url to verification
                    # - encode uid
                    # - token

                    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                    domain = get_current_site(request).domain
                    link = reverse('activate',kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})

                    activate_url = 'http://'+domain+link

                    gmail_user = 'testediyorum123@gmail.com'
                    gmail_pwd = "goxeyehiqnwanpnc"
                    FROM = gmail_user
                    TO = email if type(email) is list else [email]
                    SUBJECT = "ACTIVATE YOUR ACCOUNT"
                    TEXT = 'Hi '+user.username+', please use this link to verify your account!\n' + activate_url

                    # Prepare actual message
                    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
                    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
                    try:
                        server = smtplib.SMTP("smtp.gmail.com", 587)
                        server.ehlo()
                        server.starttls()
                        server.login(gmail_user, gmail_pwd)
                        server.sendmail(FROM, TO, message)
                        server.close()
                        print
                        'successfully sent the mail'
                    except:
                        print
                        "failed to send mail"

                    messages.add_message(request, messages.SUCCESS,
                                         'Hesabiniz olusturuldu. Lutfen emailinize gelen link ile hesabinizi aktive ediniz.')
                    return redirect('login')
        else:
            messages.add_message(request, messages.WARNING, 'Girdiginiz parolalar uyusmuyor')
            return redirect('register')
    else:
        return render(request, 'user/register.html')


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.add_message(request, messages.SUCCESS, 'Oturumunuz kapatildi')
        return redirect('index')
    else:
        return render(request, 'user/logout.html')


class VerificationView(View):
    def get(self, request, uidb64, token):

        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('login')
            else:
                user.is_active = True
                user.save()

            messages.success(request,'Hesabiniz basari ile aktive edildi, simdi giris yapabilirsiniz!')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')