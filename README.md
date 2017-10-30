## Necessary variables

SECRET_KEY: Replace this in settings.py and keep it secret.  
PGUSER and PGPASSWORD: User and password for the Postgres database. These are passed in via environment variable.  
SOCIAL_AUTH_STEAM_API_KEY: This is the API key for the Steam API. You can get this from Steam and pass it in
via environment variable.

## Necessary database objects

Create an admin user with `python manage.py superuser`  
Add 4 Week objects for each week. These are needed because a game can appear in several weeks.  
Add a voting period for each voting period. Voting will be unlocked during these times.  

## Management commands

`createpicks`: Obsolete. Used to parse picks from forum entries.  
`importgames`: Initially imports games from the SteamProphet site. Run `updategames` next.  
`printoverduegames`: Prints overdue games.  
`printupcominggames`: Prints upcoming games to be posted into the forum.  
`updategames`: Updates all games in the DB. Run this after `importgames` as well as once per day.  
`updateplayers`: Updates player's histories. Run this once per day.  
