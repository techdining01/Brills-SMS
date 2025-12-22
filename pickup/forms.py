from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class PickupCodeGenerationForm(forms.Form):
    """
    Form used by parents to select the student for whom the code is generated.
    """
    student = forms.ModelChoiceField(
        queryset=User.objects.none(), 
        label="Select Child for Pickup",
        empty_label="--- Select a Student ---",
        widget=forms.Select(attrs={'class': 'w-full p-3 border border-gray-300 rounded-lg'})
    )

    def __init__(self, *args, **kwargs):
        self.parent_user = kwargs.pop('parent_user')
        super().__init__(*args, **kwargs)
        
        # Filter the queryset to only show students linked to the current parent
        # This relies on the 'children' related_name defined in accounts/models.py
        self.fields['student'].queryset = self.parent_user.children.filter(
            role=User.Role.STUDENT # Ensure only student roles are returned
        ).order_by('last_name')