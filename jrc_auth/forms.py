import redis

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.forms.fields import EmailField, CharField
from django.forms import ValidationError
from uuid import uuid4

r = redis.StrictRedis(host='localhost', port=6379, db=1)


def send_activation_email(user):
    token = r.get(user.email)
    if not token:
        token = str(uuid4())
        r.set(user.email, token)
        r.expire(user.email, 86400)  # Expire in 24h
        r.set(token, user.email)
        r.expire(token, 86400)
    txt = "Click the following link to activate your JrC-account:\n" + \
          "https://auth.jrc.no/activate/" + token + "/"
    msg = EmailMultiAlternatives(
        subject="Please activate your JrC account",
        body=txt,
        from_email="Junior Consulting AS <no-reply@mg.juniorconsulting.no",
        to=[user.email],
        reply_to=["Junior Consulting AS - IT <it@juniorconsulting.no"]
    )
    msg.tags = ["activation"]
    msg.send()


class JrCEmailField(EmailField):
    def validate(self, value):
        super(JrCEmailField, self).validate(value)
        domain = value.split('@')[1]
        if domain != 'juniorconsulting.no':
            raise ValidationError(
                "A juniorconsulting.no email-adress is required",
                code='invalid'
            )


class JrCUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")
        field_classes = {"username": CharField, "email": JrCEmailField}

    def save(self, commit=True):
        user = super(JrCUserCreationForm, self).save(commit=False)
        user.is_active = False
        try:
            send_activation_email(user)
        except:
            pass
        if commit:
            user.save()
        return user
