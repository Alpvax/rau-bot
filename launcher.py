def unimport(*names):
    import sys
    if not names:
        import os.path
        names = [k for k,v in sys.modules.items() if not v or (hasattr(v, "__file__") and os.path.exists(os.path.basename(v.__file__)))]
    for name in names:
        del sys.modules[name]

def setupLogging(name=__name__, logFile=None):
    if not logFile:
        logFile = name + ".log"
    import logging, sys
    rootLogger = logging.getLogger("")
    rootLogger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(logFile)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    rootLogger.addHandler(fh)
    # create console handler with a higher log level
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.ERROR)
    ch.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
    rootLogger.addHandler(ch)
    return logging.getLogger(name)

logger = setupLogging(logFile="rau-bot.log")


class Controller(object):
    def __init__(self, *setup):
        from threading import Event
        self.stop_event = Event()
        self.start_event = Event()
        self.running = False
        self.updater = None
        self.setupFuncs = setup or []
        
    def _run(self):
        from time import sleep
        while self.running:
            if self.stop_event.isSet():
                self.stop_event.clear()
                print("Stopping...")
                if self.updater:
                    self.updater.stop()
                    self.updater = None
                print("Bot stopped")
                unimport("handlers", "credentials")
            if self.start_event.isSet():
                self.start_event.clear()
                if not self.updater:
                    self.setup()
                print("Starting rau_bot in long polling mode...")
                self.updater.start_polling()
            sleep(1)
                
    def setup(self):
        [func() for func in self.setupFuncs]
        import credentials, handlers
        from telegram.ext import Updater
        self.updater = Updater(credentials.TOKEN)
        self.updater.dispatcher.add_error_handler(handlers.error)
        self.addHandler(*handlers.ALL_HANDLERS)
        from signal import signal, SIGINT, SIGTERM, SIGABRT
        for sig in (SIGINT, SIGTERM, SIGABRT):
            signal(sig, self.updater.signal_handler)
        
    def addHandler(self, *handlers):
        for obj in handlers:
            if hasattr(obj, "handler"):
                self.updater.dispatcher.add_handler(obj.handler)
                
    def start(self):
        self.start_event.set()
        if not self.running:
            self.running = True
            self._run()
        
    def stop(self):
        self.stop_event.set()
        self.running = False
        
    def reload(self):
        self.stop_event.set()
        self.start_event.set()

def createBotStateHandler():
    from handlers import ConversationHandler, CommandHandler, RegexHandler
    from telegram import ReplyKeyboardMarkup
    bot_state_handler = ConversationHandler()
    bot_state_handler.handlerHelpers = []
    
    def bot_state_helper(matcher=None):
        def decorator(func):
            func.matcher = matcher or (lambda cmd: (cmd[0].lower() == func.__name__, (len(cmd) > 1 and cmd[1:]) or []))
            bot_state_handler.handlerHelpers.append(func)
            return func
        return decorator
        
    @bot_state_helper()
    def terminate(bot, update, args):
        update.message.reply_text("Stopping bot! Cannot be restarted remotely!\nAre you sure?", reply_markup=ReplyKeyboardMarkup([["Yes", "No"]], one_time_keyboard=True))
        return verifystop.state
            
    @bot_state_helper()
    def reload(bot, update, args):
        update.message.reply_text("Reloading bot (args=\"{0}\"). If something goes wrong, you will need to manually restart!\nAre you sure?".format(args), reply_markup=ReplyKeyboardMarkup([["Yes", "No"]], one_time_keyboard=True))
        return verifyreload.state

    @bot_state_handler.entry(lambda f: CommandHandler(f.__name__, f, pass_args=True))
    def bot_state(bot, update, **args):
        command = args["args"]
        if len(command) < 1:
            update.message.reply_text("No command recognised!")
            return ConversationHandler.END
        if update.message.from_user.username.lower() != "alpvax":
            err = "User {0} attempted to change bot state ({1})!".format(update.message.from_user.name, " ".join(command))
            update.message.reply_text(err)
            getLogger().warn(err)
            return ConversationHandler.END
        
        for helper in bot_state_handler.handlerHelpers:
            m, cmdargs = helper.matcher(command)
            if m:
                return helper(bot, update, cmdargs)
            
        update.message.reply_text("Command \"{0}\" not recognised!".format(" ".join(args["args"])))
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
            controller.reload()

if __name__=="__main__":
    #createBotStateHandler()
    controller = Controller(createBotStateHandler)
    #import thread
    #thread.start_new_thread(lambda controller: [raw_input(), controller.reload()], (controller,))
    controller.start()