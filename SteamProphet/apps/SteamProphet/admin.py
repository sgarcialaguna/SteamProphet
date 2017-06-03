from django.contrib import admin

from .models import Game, Player, Pick

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('appID', 'name', 'releaseDate', 'price')

admin.site.register(Player)
admin.site.register(Pick)