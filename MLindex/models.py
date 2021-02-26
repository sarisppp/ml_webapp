from django.db import models
from django import forms

class Member(models.Model):
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=20)


class MemberForm(forms.ModelForm):
    comfirm_pswd = forms.CharField(
        label = 'ใส่รหัสผ่านซ้ำอีกครั้ง',
        widget = forms.PasswordInput()
    )

    class Meta:
        model = Member
        fields = '__all__'
        labels = {
            'firstname' : 'ชื่อ',
            'lastname' : 'นามสกุล',
            'email' : 'อีเมล',
            'password' : 'รหัสผ่าน'
            }
        widgets = {
            'password' : forms.PasswordInput(render_value=True)
            }