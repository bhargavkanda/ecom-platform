from django import forms

class NameForm(forms.Form):
    name = forms.CharField(label='name', min_length=5,max_length=30)
    phone = forms.CharField(label='phone', min_length=10,max_length=20)
    email = forms.EmailField(label='email', min_length=5,max_length=50)
    city = forms.CharField(label='city', min_length=2,max_length=30)
