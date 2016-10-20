class updateHandler(object):
    def __init__(self, handlerConstructor):
        self.constructHandler = handlerConstructor
        import sys
        self.module = sys.modules[self.__module__]
        if not hasattr(self.module, "ALL_HANDLERS"):
            setattr(self.module, "ALL_HANDLERS", [])
        
    def __call__(self, callable):
        handler = self.constructHandler(callable)
        callable.handler = handler
        self.module.ALL_HANDLERS.append(callable)
        return callable
        
class ConversationHandler(object):
    END = -1
    def __init__(self):
        self.entry_points = []
        self.states = {}
        self.fallbacks = []
        from telegram.ext import ConversationHandler as _ConvHandler
        import sys
        self.module = sys.modules[self.__module__]
        if not hasattr(self.module, "ALL_HANDLERS"):
            setattr(self.module, "ALL_HANDLERS", [])
        self.module.ALL_HANDLERS.append(self)
        
    def entry(self, handlerConstructor):
        def decorator(func):
            self.entry_points.append(handlerConstructor(func))
            return func
        return decorator
        
    def state(self, index, handlerConstructor):
        def decorator(func):
            func.state = index
            try:
                self.states[index].append(handlerConstructor(func))
            except KeyError:
                self.states[index] = [handlerConstructor(func)]
            return func
        return decorator
        
    def fallback(self, handlerConstructor):
        def decorator(func):
            self.fallbacks.append(handlerConstructor(func))
            return func
        return decorator
        
    @property
    def handler(self):
        from telegram.ext import ConversationHandler as _ConvHandler
        return _ConvHandler(entry_points=self.entry_points, states=self.states, fallbacks=self.fallbacks)
        
###        # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
###    conv_handler = ConversationHandler(
###        entry_points=[CommandHandler('start', start)],
###
###        states={
###            GENDER: [RegexHandler('^(Boy|Girl|Other)$', gender)],
###
###            PHOTO: [MessageHandler([Filters.photo], photo),
###                    CommandHandler('skip', skip_photo)],
###
###            LOCATION: [MessageHandler([Filters.location], location),
###                       CommandHandler('skip', skip_location)],
###
###            BIO: [MessageHandler([Filters.text], bio)]
###        },
###
###        fallbacks=[CommandHandler('cancel', cancel)]
###    )

def getLogger():
    global logger
    try:
        return logger
    except:
        import logging
        logger = logging.getLogger("__main__")
        return logger
        
def error(bot, update, error):
    getLogger().warn('Update "%s" caused error "%s"' % (update, error))
    

#=======Use from handlers import * to import========#
#======= all handler types from telegram.ext========#
from telegram.ext import CallbackQueryHandler, ChosenInlineResultHandler, CommandHandler, InlineQueryHandler, MessageHandler, RegexHandler, StringCommandHandler, StringRegexHandler, TypeHandler

__all__ = ["CallbackQueryHandler", "ChosenInlineResultHandler", "CommandHandler", "InlineQueryHandler", "MessageHandler", "RegexHandler", "StringCommandHandler", "StringRegexHandler", "TypeHandler", "ALL_HANDLERS", "updateHandler", "ConversationHandler"]
    
#===================================================#
#==================Actual Handlers==================#
    
from telegram import InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup#, ForceReply
from uuid import uuid4
    
@updateHandler(lambda f: CommandHandler(f.__name__, f))
def start(bot, update):
    user = update.message.from_user
    bot.sendMessage(update.message.chat_id, text="Hi {}!\nHow are you?".format(('{} {}'.format(user.first_name, user.last_name)) if user.last_name else user.first_name))#, reply_to_message_id=update.message.message_id, reply_markup=ForceReply(selective=True))

@updateHandler(lambda f: CommandHandler(f.__name__, f))
def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!\n<Help topics>')

@updateHandler(lambda f: CommandHandler(f.__name__, f, pass_args=True))#Use "(MessageHandler, [Filters.text])" to recognise any (text) response
def echo(bot, update, **args):
    bot.sendMessage(update.message.chat_id, text=" ".join(args["args"]))
        
#@updateHandler(lambda f: InlineQueryHandler(f, pattern="\s*/echo\s+(?P<text>.+)", pass_groupdict=True))
#def inlineEcho(bot, update, **args):
#    pass
