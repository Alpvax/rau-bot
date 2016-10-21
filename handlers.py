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

def getLogger(name=__name__):
    global logger
    try:
        return logger
    except:
        import logging
        logger = logging.getLogger(name)
        return logger
        
def error(bot, update, error):
    getLogger("__main__").warn('Update "%s" caused error "%s"' % (update, error))
    

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

#================"/bot_state handler"===============#
def createBotStateHandler(controller):
    """Call this to set up handler for /bot_state <command> [args]"""
    bot_state_handler = ConversationHandler()
    bot_state_handler.handlerHelpers = []
    
    def bot_state_helper(matcher=None):
        def decorator(func):
            func.matcher = matcher or (lambda cmd: (cmd[0].lower() == func.__name__, (len(cmd) > 1 and cmd[1:]) or []))
            bot_state_handler.handlerHelpers.append(func)
            return func
        return decorator
        
    verifyKeyboard = ReplyKeyboardMarkup([["Yes", "No"]], resize_keyboard=True, one_time_keyboard=True, selective=True)
    logger = getLogger("bot_state_handler")
        
    @bot_state_helper()
    def terminate(bot, update, args):
        update.message.reply_text("Stopping bot! Cannot be restarted remotely!\nAre you sure?", reply_markup=verifyKeyboard)
        return verifystop.state
            
    @bot_state_helper()
    def reload(bot, update, args):
        update.message.reply_text("Reloading bot. If something goes wrong, you will need to manually restart!\nAre you sure?".format(args), reply_markup=verifyKeyboard)
        return verifyreload.state
        
    @bot_state_helper(lambda cmd: (cmd[0].lower() == "git", cmd))
    def git(bot, update, args):
        from subprocess32 import check_output, STDOUT#subprocess32 adds support for timeout
        update.message.reply_text(check_output(args, stderr=STDOUT, timeout=20), disable_web_page_preview=True)
        return ConversationHandler.END
        
    @bot_state_helper()
    def handlers(bot, update, args):
        update.message.reply_text(str(["{0} ({0.handler})".format(h) for h in ALL_HANDLERS]))
        return ConversationHandler.END

    @bot_state_handler.entry(lambda f: CommandHandler(f.__name__, f, pass_args=True))
    def bot_state(bot, update, **args):
        command = args["args"]
        if update.message.chat.type != "private":
            update.message.reply_text("That command can only be run in a <a href='telegram.me/{0}'>private chat</a>.".format(bot.username), parse_mode="HTML", disable_web_page_preview=True)
            return ConversationHandler.END
        if len(command) < 1:
            update.message.reply_text("No command recognised!")
            return ConversationHandler.END
        if update.message.from_user.username.lower() != "alpvax":
            err = "User {0} attempted to change bot state ({1})!\nPERMISSION DENIED!".format(update.message.from_user.name, " ".join(command))
            update.message.reply_text(err)
            logger.warn(err)
            return ConversationHandler.END
        
        for helper in bot_state_handler.handlerHelpers:
            m, cmdargs = helper.matcher(command)
            if m:
                return helper(bot, update, cmdargs)
            
        update.message.reply_text("Command \"{0}\" not recognised!".format(" ".join(command)))
        return ConversationHandler.END
            
        
    @bot_state_handler.state("terminate", lambda f: RegexHandler('^(Yes|No)$', f))
    def verifystop(bot, update):
        update.message.reply_text("Bot Stopped! Manual restart required.")
        if update.message.text == "Yes":
            controller.stop()
            
    @bot_state_handler.state("reload", lambda f: RegexHandler('^(Yes|No)$', f))
    def verifyreload(bot, update):
        update.message.reply_text("Reloading bot.")
        if update.message.text == "Yes":
            controller.startData.setdefault("notifyChats", [])
            if update.message.chat_id not in controller.startData["notifyChats"]:
                controller.startData["notifyChats"].append(update.message.chat_id)
            controller.reload()