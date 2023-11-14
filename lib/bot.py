
import asyncio
import threading

from twitchio.ext import commands


class Bot(commands.Bot):

	def __init__(self, config):
		# Initialise our Bot with our access token, prefix and a list of channels to join on boot...
		super().__init__(token=config["TWITCH"]["ACCESS_TOKEN"], prefix='?', initial_channels=[config["TWITCH"]["CHANNEL"]])
		self.config = config

	async def event_ready(self):
		# We are logged in and ready to chat and use commands...
		print(f'Logged in as | {self.nick}')
		print(f'User id is | {self.user_id}')

	async def repeat_message_loop(self, message, period_in_seconds):
		while True:
			await self.get_channel(self.config["TWITCH"]["CHANNEL"]).send(message)
			await asyncio.sleep(period_in_seconds)
			
	def start_repeat_message_task(self, message, period_in_seconds):
		return self.loop.create_task(self.repeat_message_loop(message, period_in_seconds))
		
	def stop_repeat_message_task(self, task):
		task.cancel()
		
class BotThread(threading.Thread):
	def __init__(self, config):
		threading.Thread.__init__(self)
		self.daemon = True
		self.bot = Bot(config)

	def run(self):
		self.bot.run()
		
	def get_bot(self):
		return self.bot
        