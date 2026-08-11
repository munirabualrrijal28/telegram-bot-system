from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
app, created = SocialApp.objects.get_or_create(provider='google', defaults={'name': 'Google Login', 'client_id': 'dummy', 'secret': 'dummy'})
site, _ = Site.objects.get_or_create(id=1, defaults={'domain': 'mytelebot.com', 'name': 'mytelebot.com'})
app.sites.add(site)
print("SocialApp successfully seeded!")
