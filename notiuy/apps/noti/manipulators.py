from django.contrib.auth.models import User
from django import forms
from django.core import validators
from models import User

user_validator = validators.MatchesRegularExpression(r'^[a-zA-Z0-9]{3,15}$', _("Must be 3-15 alphanumeric characters"))
pass_validator = validators.AlwaysMatchesOtherField('password2', _("Password fields don't match"))

class RegisterManipulator(forms.Manipulator):
    def __init__(self):
        self.fields = (
            forms.TextField(field_name="username", length=15, maxlength=15, is_required=True,
                validator_list=[user_validator, self.isValidUser]),
            forms.EmailField(field_name="email", length=30, is_required=True,
                validator_list=[self.isValidUserEmail]),
            forms.PasswordField(field_name="password1", length=30, maxlength=30, is_required=True,
                validator_list=[pass_validator]),
            forms.PasswordField(field_name="password2", length=30, maxlength=30),
        )

    def save(self, new_data):
        user = User.objects.create_user(new_data['username'], new_data['email'], new_data['password1'])
        user.save()

    def isValidUser(self, field_data, all_data):
        if (User.objects.filter(username__iexact=field_data)):
            raise validators.ValidationError, _("Username exists")

    def isValidUserEmail(self, field_data, all_data):
        if (User.objects.filter(email__iexact=field_data)):
            raise validators.ValidationError, _("Email already in use")


class ProfileManipulator(forms.Manipulator):
    def __init__(self, user_id):
        self.user = User.objects.get(id=user_id)

        favs = [(fav.id, fav.name) for fav in self.user.favorites.all()]

        self.fields = (
            forms.TextField(field_name="username", length=15, maxlength=15, is_required=True,
                validator_list=[user_validator, self.isValidUser]),
            forms.EmailField(field_name="email", length=30, is_required=True,
                validator_list=[self.isValidUserEmail]),
            forms.TextField(field_name="first_name", length=30, maxlength=50),
            forms.TextField(field_name="last_name", length=30, maxlength=50),
            forms.PasswordField(field_name="password1", length=30, maxlength=30,
                validator_list=[pass_validator]),
            forms.PasswordField(field_name="password2", length=30, maxlength=30),
            forms.SelectMultipleField(field_name="favs", choices=favs, size=6),
        )

    def flatten_data(self):
        return self.user.__dict__

    def isValidUser(self, field_data, all_data):
        if (User.objects.filter(username__iexact=field_data).exclude(id=self.user.id)):
            raise validators.ValidationError, _("Username exists")

    def isValidUserEmail(self, field_data, all_data):
        if (User.objects.filter(email__iexact=field_data).exclude(id=self.user.id)):
            raise validators.ValidationError, _("Email already in use")

    def save(self, new_data):
        if new_data['password1'] and self.user.password != new_data['password1']:
            self.user.set_password(new_data['password1'])
        self.user.username = new_data['username']
        self.user.email = new_data['email']
        self.user.first_name = new_data['first_name']
        self.user.last_name = new_data['last_name']
        self.user.save()

        if new_data['favs']:
            self.user.favorites.filter(id__in=new_data['favs']).delete()


class FavoriteManipulator(forms.Manipulator):
    def __init__(self, user_id):
        self.user = User.objects.get(id=user_id)

        self.fields = (
            forms.TextField(field_name="name", length=30, maxlength=50, is_required=True),  # TODO: add isSlug validator
            forms.HiddenField(field_name="path"), # TODO: add validators for path
        )

    def save(self, new_data):
        self.user.favorites.create(name=new_data['name'], path=new_data['path'])

