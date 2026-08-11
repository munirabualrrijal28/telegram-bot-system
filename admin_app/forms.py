from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors',
            'placeholder': 'Admin Username',
            'autocomplete': 'off'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors',
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        })
    )

class BroadcastForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors',
            'placeholder': 'Notification Title'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors',
            'placeholder': 'Message content...',
            'rows': 4
        })
    )
    notification_type = forms.ChoiceField(
        choices=[
            ('in_app', 'In-App Notification'),
            ('email', 'Email'),
            ('both', 'Both (Email + In-App)'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'
        })
    )

class SubscriptionUpdateForm(forms.Form):
    plan_name = forms.ChoiceField(
        choices=[
            ('Free', 'Free Plan'),
            ('Pro', 'Pro Plan'),
            ('Max', 'Max Plan'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'
        })
    )
    status = forms.ChoiceField(
        choices=[
            ('active', 'Active'),
            ('cancelled', 'Cancelled'),
            ('expired', 'Expired'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'
        })
    )

class ActivationCodeForm(forms.Form):
    plan_name = forms.ChoiceField(
        label='Subscription Plan',
        choices=[
            ('Free', 'Free Plan'),
            ('Free Trial', 'Free Trial (7 Days)'),
            ('Pro', 'Pro Plan'),
            ('Max', 'Max Plan'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'
        })
    )
    code_type = forms.ChoiceField(
        label='Code Type',
        choices=[
            ('general', 'General Code (Any User)'),
            ('user_specific', 'User-Specific Code'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'text-primary-600 focus:ring-primary-500'
        }),
        initial='general'
    )
    target_user = forms.CharField(
        label='Target User ID',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors',
            'placeholder': 'Enter user ID (for user-specific codes only)'
        })
    )
    expires_at = forms.DateTimeField(
        label='Expiration Date (Optional)',
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'
        })
    )
