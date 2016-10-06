import telegram
from flask import Flask, request, json
from google.appengine.api import urlfetch
app = Flask(__name__)
app.config['DEBUG'] = True

from credentials import TOKEN, APP_URL

global bot
bot = telegram.Bot(token=TOKEN)

from telegram.ext import Dispatcher
dispatcher = None

def setup():
    '''GAE DISPATCHER SETUP'''

    global dispatcher
    # Note that update_queue is setted to None and
    # 0 workers are allowed on Google app Engine (If not-->Problems with multithreading)
    dispatcher = Dispatcher(bot=bot, update_queue=None, workers=0)
    
    import handlers
    
    # ---Register handlers---
    for callback in handlers:
        if callback.hasattr("handler"):
            dispatcher.add_handler(callback.handler)

#    # ---Register handlers here---
#    dispatcher.add_handler(CommandHandler("start", start))
#    dispatcher.add_handler(CommandHandler("help", help))
#    dispatcher.add_handler(MessageHandler([Filters.text], echo))
    dispatcher.add_error_handler(handlers.error)

    return dispatcher

@app.route('/' + TOKEN,methods=['POST'])
def telegram_webhook():
    if request.method == "POST":
        # retrieve the message in JSON and then transform it to Telegram object
        update = telegram.Update.de_json(request.get_json(force=True))
        
        # Manually get updates and pass to dispatcher
        dispatcher.process_update(update)
#
#        chat_id = update.message.chat.id
#
#        # Telegram understands UTF-8, so encode text for unicode compatibility
#        text = update.message.text.encode('utf-8')
#
#        # repeat the same message back (echo)
#        bot.sendMessage(chat_id=chat_id, text=text)

    return 'ok'

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    setup()
    s = bot.setWebhook(APP_URL + '/' + TOKEN)
    if s:
        return "WebHook setup ok"
    else:
        return "WebHook setup failed"

@app.route('/')
def index():
    return "<!DOCTYPE html><html><head><script>window.location.href='http://telegram.me/rau_bot'</script></head> \
    <body>If you are not redirected automatically, <a href='http://telegram.me/rau_bot'>click here</a></body></html>"


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
