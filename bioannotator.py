from flask import Flask, jsonify, g, request
import redis
import pyreBloom
import time

app = Flask(__name__)


@app.before_request
def before_request():
  g.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
  g.bloom = pyreBloom.pyreBloom('gene_symbols', 100000, 0.01)
  if app.debug:
    print "start request"
    g.start = time.time()


@app.teardown_request
def teardown_request(exception=None):
  if app.debug:
    diff = time.time() - g.start
    print "response time: %f" % (diff)
    print "end request"


@app.route('/annotate', methods=['POST'])
def annotate():

  # get a unique set of the words in the article that are
  # 1. longer than one character
  # 2. all caps
  # 3. encoded as utf-8
  words = set([x.upper().encode('UTF-8')
               for x in request.get_json()["words"]
               if len(x) > 1])

  symbols = {}

  for found_word in g.bloom.contains(words):
    symbol = g.redis.get(found_word)

    if symbol:
      symbols[symbol] = g.redis.hgetall("h_%s" % symbol)

  if app.debug:
    print "article length: %d" % (len(words))
    print "found entities: %d" % (len(symbols))

  return jsonify(symbols)


@app.route('/symbol/<symbol>', methods=['GET'])
def symbol(symbol):
  symbol = symbol.upper()
  symbol = g.redis.get(symbol)
  return jsonify(g.redis.hgetall("h_%s" % (symbol)))


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=80, debug=True)
