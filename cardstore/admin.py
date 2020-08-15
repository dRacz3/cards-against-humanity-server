from django.contrib import admin

from cardstore.models import WhiteCard, BlackCard

class CardAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['card_text']}),
    ]
    list_display = ('card_text', 'package')


admin.site.register(WhiteCard, CardAdmin)
admin.site.register(BlackCard, CardAdmin)
