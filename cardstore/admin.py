from django.contrib import admin

from cardstore.models import WhiteCard, BlackCard, DeckMetaData

class CardAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['text', 'deck', 'icon']}),
    ]
    list_display = ('text', 'deck', 'icon')
    list_filter = ['deck']

class BlackCardAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['text', 'deck', 'icon', 'pick']}),
    ]
    list_display = ('text', 'deck', 'icon', 'pick')

    list_filter = ['pick', 'deck']

admin.site.register(WhiteCard, CardAdmin)
admin.site.register(BlackCard, BlackCardAdmin)
admin.site.register(DeckMetaData)
