# Discord Todo Bot

## Install Steps
1. Checkout branch
1. Create a venv and install requirements.txt
```
python3.11 -mvenv .venv
pip install -r requirements.txt
```
1. Create a discord bot and invite to your server. [Instructions](https://discordpy.readthedocs.io/en/stable/discord.html)
1. Update .env with discord token (from prior step) and channel token (in discord, right click on the channel and copy id)
1. In mysql, create a database and a user.  The table will be automatically created.  Update the values in the .env file.

Run the file and it should connect.
