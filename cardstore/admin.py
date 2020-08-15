from django.contrib import admin

from cardstore.models import WhiteCard, BlackCard, DeckMetaData

class CardAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['text', 'deck', 'icon']}),
    ]
    list_display = ('text', 'deck', 'icon')


admin.site.register(WhiteCard, CardAdmin)
admin.site.register(BlackCard, CardAdmin)
admin.site.register(DeckMetaData)
