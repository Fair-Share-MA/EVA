from django import forms

class FileFieldForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True, 'accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, text/plain'}))
    overrides = forms.CharField(widget=forms.Textarea(attrs={'class': 'textarea', 'placeholder': '{\n"Voter ID:" ["Vote ID", "voter_id"]\n}'}), required=False)