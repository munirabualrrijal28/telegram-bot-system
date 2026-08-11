# bot/forms.py
from django import forms
from .models import FAQ, FAQCategory , BotSettings



class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['category', 'question', 'answer', 'is_active']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control'}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class FAQCategoryForm(forms.ModelForm):
    class Meta:
        model = FAQCategory
        fields = ['name', 'parent', 'keyboard_type']




class BotSettingsForm(forms.ModelForm):
    class Meta:
        model = BotSettings
        fields = [
            'workspace_name','telegram_token','bot_username','is_active',
            'welcome_message', 'fallback_message', 'start_keywords',
            'working_hours_start','working_hours_end',
            'language','show_contact_info','contact_phone','contact_address',
            'google_maps_link','enable_ai_mode'
        ]
        widgets = {
            'workspace_name': forms.TextInput(attrs={'class': 'form-control'}),
            # <-- stable id for javascript:
            'telegram_token': forms.TextInput(attrs={'id': 'botTokenInput', 'class': 'form-control', 'autocomplete': 'off'}),
            'bot_username': forms.TextInput(attrs={'class': 'form-control'}),
    
            # 
            'welcome_message': forms.Textarea(attrs={'rows':2, 'class':'form-control'}),
            'fallback_message': forms.Textarea(attrs={'rows':2, 'class':'form-control'}),
            'start_keywords': forms.Textarea(attrs={'rows':2, 'class':'form-control', 'placeholder': 'hi, hello, start, ...'}),
            'working_hours_start': forms.TimeInput(attrs={'type':'time','class':'form-control'}),
            'working_hours_end': forms.TimeInput(attrs={'type':'time','class':'form-control'}),
            'language': forms.Select(attrs={'class':'form-select'}),
            'contact_phone': forms.TextInput(attrs={'class':'form-control'}),
            'contact_address': forms.TextInput(attrs={'class':'form-control'}),
            'google_maps_link': forms.URLInput(attrs={'class':'form-control'}),
        }

