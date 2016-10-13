class simpleHandler(object):
    def __init__(self, handlerCallable, key=None, **kwargs):
        import sys
        self.module = sys.modules[self.__module__]
        if not hasattr(self.module, "ALL_HANDLERS"):
            setattr(self.module, "ALL_HANDLERS", [])
        self.handlerCallable = handlerCallable
        self.key = key
        self.kwargs = kwargs
        
    def __call__(self, callable):
        self.kwargs['callback'] = callable
        handler = self.handlerCallable(self.key or callable.__name__, **self.kwargs)
        callable.handler = handler
        self.module.ALL_HANDLERS.append(callable)
        return callable

def logger():
    global logger
    try:
        return logger
    except:
        import sys
        logger = sys.modules["__main__"].logger
        return logger
        
def error(bot, update, error):
    logger().warn('Update "%s" caused error "%s"' % (update, error))
    
#==================Actual Handlers==================#
    
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram import ForceReply
    
@simpleHandler(CommandHandler)
def start(bot, update):
    user = update.message.from_user
    bot.sendMessage(update.message.chat_id, text="Hi {}!\nHow are you?".format(('{} {}'.format(user.first_name, user.last_name)) if user.last_name else user.first_name))#, reply_to_message_id=update.message.message_id, reply_markup=ForceReply(selective=True))

@simpleHandler(CommandHandler)
def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')

@simpleHandler(CommandHandler, pass_args=True)#Use "(MessageHandler, [Filters.text])" to recognise any (text) response
def echo(bot, update, **args):
    bot.sendMessage(update.message.chat_id, text=" ".join(args["args"]))