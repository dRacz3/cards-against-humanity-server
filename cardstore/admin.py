from django.contrib import admin


# Register your models here.
from cardstore.models import WhiteCard, BlackCard

admin.site.register(WhiteCard)
admin.site.register(BlackCard)