from django import forms

class MessageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, max_length=1000)
