# The World Machine

### A discord bot based off the videogame OneShot, and built using the interactions-py library.

For more information, check out our website: https://www.theworldmachine.xyz/invite

---
## Contributing:

### Localization
In `bot/localization/locales` there are different localization files. Using `base.yaml` as a base, you are free to contribute your own language to the bot. As of current, only the `/shop`, `/interact` and `/nikogotchi` commands supports localization.

### Pull Requests
As with any other repo, pull requests and bug reporting is always welcomed.

### Crediting
Contributing in any way to the discord bot will have your name be put in the website's credits and a role assigned on the discord.

---
## Running your own instance:

### Step 1: Download Dependencies.
Download Python 3.11 and set it as your main interpreter in your code editor. To download dependencies, run this in your console:
```commandline
pip install -r requirements.txt
```
This should install all dependencies needed to run the bot.

### Step 2: config.yaml
In `bot/data` there is file called `example_config.yaml` which has information for APIs and other sensitive information that should be included. You need to create a file in the same directory called `config.yaml` with the information filled.

### Step 3: Running the bot.
If everything is done right, the bot should run.
