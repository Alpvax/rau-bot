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
        self._stop_event = Event()
        self._reload_event = Event()
        self.running = False
        self.updater = None
        self.setupFuncs = setup or []
        self.startData = {}
        
    def _run(self):
        from time import sleep
        self.running = True
        while self.running:
            if self._stop_event.isSet():#Stop controller
                self.running = False
                self._stop()
            if self._reload_event.isSet():#Stop updater
                self._reload_event.clear()
                self._stop()
                self._start()
            sleep(1)
                
    def _setup(self):
        [func(self) for func in self.setupFuncs]
        import credentials, handlers
        from telegram.ext import Updater
        self.updater = Updater(credentials.TOKEN)
        self.updater.dispatcher.add_error_handler(handlers.error)
        self.addHandler(*handlers.ALL_HANDLERS)
        from signal import signal, SIGINT, SIGTERM, SIGABRT
        for sig in (SIGINT, SIGTERM, SIGABRT):
            signal(sig, self.updater.signal_handler)
        
    def _start(self):
        if not self.updater:
            self._setup()
        print("Starting rau_bot in long polling mode...")
        self.updater.start_polling()
        for id in self.startData.get("notifyChats", []):
            self.bot.sendMessage(id, "{0} loaded.".format(self.bot.name), disable_notification=True)
        
    def _stop(self):
        print("Stopping...")
        if self.updater:
            self.updater.stop()
            self.updater = None
        print("Bot stopped")
        unimport("handlers", "credentials")
        
    @property
    def bot(self):
        return self.updater.bot
        
    def addHandler(self, *handlers):
        for obj in handlers:
            if hasattr(obj, "handler"):
                self.updater.dispatcher.add_handler(obj.handler)
                
    def start(self):
        self._start()
        if not self.running:
            self._run()
        
    def stop(self):
        self._stop_event.set()
        
    def reload(self):
        self._reload_event.set()
        
def createBotStateHandler(controller):
    import handlers
    handlers.createBotStateHandler(controller)

if __name__=="__main__":
    controller = Controller(createBotStateHandler)
    #import thread
    #thread.start_new_thread(lambda controller: [raw_input(), controller.reload()], (controller,))
    controller.start()