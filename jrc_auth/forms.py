from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.fields import EmailField, CharField
from django.forms import ValidationError


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
        if commit:
            user.save()
        return user
