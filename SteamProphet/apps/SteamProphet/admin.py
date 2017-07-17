import bulk_admin
from django.contrib import admin

from .models import Game, Player, Pick, VotingPeriod


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('appID', 'name', 'releaseDate', 'price')

@admin.register(Pick)
class PickAdmin(bulk_admin.BulkModelAdmin):
    pass

admin.site.register(Player)

admin.site.register(VotingPeriod)