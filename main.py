import telegram

from credentials import TOKEN

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

def addHandler(dispatcher, *handlers):
    for obj in handlers:
        if hasattr(obj, "handler"):
            dispatcher.add_handler(obj.handler)
        
def main():
    from telegram.ext import Updater
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    import handlers
    dispatcher.add_error_handler(handlers.error)
    addHandler(dispatcher, *handlers.ALL_HANDLERS)
    
    updater.start_polling()
    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    
if __name__ == "__main__":
    main()