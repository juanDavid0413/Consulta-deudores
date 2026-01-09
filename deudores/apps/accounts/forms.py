from django import forms
from django.contrib.auth.models import User, Group


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)



class UserCreateForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=(('admin', 'Administrador'), ('consultor', 'Consultor'))
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            group = Group.objects.get(name=self.cleaned_data['role'])
            user.groups.add(group)

        return user
