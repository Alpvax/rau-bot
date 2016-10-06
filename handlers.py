def simpleHandler(func, handlerCallable, key=None, **kwargs):
    kwargs['callback'] = func
    handler = handlerCallable(key or func.__name__, **kwargs)
    func.handler = handler
    return func

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))
    
from telegram.ext import CommandHandler, MessageHandler, Filters
    
@simpleHandler(CommandHandler)
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')

@simpleHandler(CommandHandler)
def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')

@simpleHandler(MessageHandler, Filters.text)
def echo(bot, update):
    bot.sendMessage(update.message.chat_id, text=update.message.text)