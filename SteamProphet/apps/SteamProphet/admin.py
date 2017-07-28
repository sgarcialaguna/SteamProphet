import bulk_admin
from django.contrib import admin

from .models import Game, Player, Pick, VotingPeriod, Week


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('appID', 'name', 'weeks', 'releaseDate', 'price')

    def get_weeks(self, obj):
        return ', '.join([str(week.week) for week in obj.week.all()])

@admin.register(Pick)
class PickAdmin(bulk_admin.BulkModelAdmin):
    pass

admin.site.register(Player)

admin.site.register(VotingPeriod)

admin.site.register(Week)
