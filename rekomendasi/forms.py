from django import forms


class CurhatForm(forms.Form):
    """Form untuk menerima curhatan/perasaan pengguna."""
    curhat = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'curhat-input',
            'placeholder': 'Ceritakan perasaanmu... Misalnya: "Aku merasa nggak setara sama dia, rasanya sedih banget..."',
            'rows': 4,
        }),
        label='',
        required=False,
    )
    mood_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
    )
