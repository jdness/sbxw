AVATAR_CHOICES = (('1','option1'), ('2','option2'), ('3','option3'), 
('4','option4'))

class RegistrationForm(forms.Form):
    avatar = ChoiceField(widget=RadioSelect, choices=AVATAR_CHOICES)
