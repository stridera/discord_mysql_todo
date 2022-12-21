import discord
from discord import app_commands
from typing import Optional

from mysql_helper import MySqlDatabase
from config import Config


class TodoClient(discord.Client):
    def __init__(self, guild, intents: discord.Intents):
        super().__init__(intents=intents)
        self.guild = discord.Object(id=guild)  # replace with your guild id
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=self.guild)
        await self.tree.sync(guild=self.guild)


def main():
    config = Config()
    intents = discord.Intents.default()
    client = TodoClient(config.guild, intents=intents)
    db = MySqlDatabase(config.host, config.user, config.password, config.database)

    async def add_task(interaction: discord.Interaction, task_type: str,  task: str):
        """Adds a task to the todo list."""
        try:
            last_id = db.execute(f"INSERT INTO todo (task_type, task, requested_by) VALUES (%s, %s, %s)",
                                 (task_type, task, interaction.user.name))
            await interaction.response.send_message(f'Added {task_type}: [{last_id}] {task}')
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}')

    async def list_tasks(interaction: discord.Interaction, tasks):
        """Lists all tasks in the todo list."""
        if len(tasks) == 0:
            await interaction.response.send_message('No tasks found')
            return

        response = "Type\tID\tTask\tRequested by\n-----------------------------------------------------\n"
        for task in tasks:
            response += f'{task[1]}\t{task[0]}\t{task[2]}\t{task[3]}\n'

        await interaction.response.send_message(response)

    @client.event
    async def on_ready():
        print(f'Logged in as {client.user} (ID: {client.user.id})')
        print('------')

    @client.tree.command()
    @app_commands.describe(task='The bug you want to add to the todo list')
    async def bug(interaction: discord.Interaction, task: str):
        """Adds a bug to the todo list."""
        await add_task(interaction, 'bug', task)

    @client.tree.command()
    @app_commands.describe(task='The typo you want to add to the todo list')
    async def typo(interaction: discord.Interaction, task: str):
        """Adds a typo to the todo list."""
        await add_task(interaction, 'typo', task)

    @client.tree.command()
    @app_commands.describe(task='The wishlist (enhancement) you want to add to the todo list')
    async def wish(interaction: discord.Interaction, task: str):
        """Adds a wish to the todo list."""
        await add_task(interaction, 'wish', task)

    @client.tree.command()
    @app_commands.describe(type='The type of task you want to list')
    async def list(interaction: discord.Interaction, type: Optional[str]):
        """Lists all tasks of a given type."""

        try:
            if type is None:
                tasks = db.fetch(f"SELECT * FROM todo WHERE completed = FALSE")
            else:
                if type not in ['bug', 'typo', 'wish']:
                    await interaction.response.send_message(f'Error: Unknown type {type}')
                    return
                tasks = db.fetch(f"SELECT * FROM todo WHERE completed = FALSE AND task_type = %s", (type,))

            await list_tasks(interaction, tasks)

        except Exception as e:
            await interaction.response.send_message(f'Error: {e}')

    @client.tree.command()
    @app_commands.describe(task_id='The id of the task you want to show.')
    async def show(interaction: discord.Interaction, task_id: int):
        """Shows specific tasks."""
        if task_id is None:
            await interaction.response.send_message(f'Error: No task_id specified')
            return

        try:
            task = db.fetch_one(f"SELECT * FROM todo where id = %s", (task_id,))

            if not task:
                await interaction.response.send_message(f'Error: Task {task} not found')
                return

            response = f"Task {task[0]}\n"
            response += f"Type: {task[1]}\n"
            response += f"Task: {task[2]}\n"
            response += f"Requested by: {task[3]}\n"
            response += f"Completed: {task[4]}\n"
            response += f"Created at: {task[5]}\n"
            await interaction.response.send_message(response)

        except Exception as e:
            await interaction.response.send_message(f'Error: {e}')

    @client.tree.command()
    async def listall(interaction: discord.Interaction):
        """Lists all tasks."""
        try:
            tasks = db.fetch(f"SELECT * FROM todo WHERE completed = FALSE")
            await list_tasks(interaction, tasks)
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}')

    @client.tree.command()
    @app_commands.describe(type='The type of task you want to list')
    async def listcompleted(interaction: discord.Interaction, type: Optional[str]):
        """Lists all completed tasks of a given type."""
        try:
            if type is None:
                tasks = db.fetch(f"SELECT * FROM todo WHERE completed = TRUE")
            else:
                if type not in ['bug', 'typo', 'wish']:
                    raise Exception('Invalid task type')
                tasks = db.fetch(f"SELECT * FROM todo WHERE task_type = %s AND completed = TRUE", (type,))
            await list_tasks(interaction, tasks)
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}')

    @client.tree.command()
    @app_commands.describe(task_id='The _id id you want to mark as completed')
    async def done(interaction: discord.Interaction, task_id: str):
        """Marks a task_id as completed."""
        try:
            db.execute(f"UPDATE todo SET completed = TRUE WHERE id = %s", (task_id,))
            await interaction.response.send_message(f'Marked {task_id} as completed')
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}')

    @client.tree.command()
    @app_commands.describe(task_id='The task you want to mark as not completed')
    async def undone(interaction: discord.Interaction, task_id: str):
        """Marks a task_id as not completed."""
        try:
            db.execute(f"UPDATE todo SET completed = FALSE WHERE id = %s", (task_id,))
            await interaction.response.send_message(f'Marked {task_id} as not completed')
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}')

    client.run(config.token)


if __name__ == '__main__':
    main()
