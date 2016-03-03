from flask import Flask, request, json
from google.appengine.api import urlfetch
app = Flask(__name__)
app.config['DEBUG'] = True

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

TOKEN = "227529011:AAFXpWknCbej9cSdlA-Ik-ju9RICjiZr6Ww"
BASE_URL = "https://api.telegram.org/bot" + TOKEN + "/"

@app.route('/' + TOKEN,methods=['POST'])
def telegram_webhook():
    data = json.loads(request.data)
    url = BASE_URL + "sendmessage?chat_id=%s&text=%s" % (-135399380, "Response")
    try:
        result = urlfetch.fetch(url, validate_certificate=True)
        return(result.read())
    except urllib2.URLError:
        logging.exception('Caught exception fetching url')
    return "OK\n" + request.data

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
