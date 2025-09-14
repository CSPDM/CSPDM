from telegram.ext import filters

start_handler = CommandHandler(command="start", callback=start, filters=filters.ChatType.PRIVATE)
application.add_handler(start_handler)