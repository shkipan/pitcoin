import flask
from flask import jsonify, request, make_response

app = flask.Flask(__name__)
app.config["DEBUG"] = True

data = {}

data['blocks'] = []
data['ppool'] = []
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Pitcoin web api</h1>
    <p>A prototype API for mastering bitcoin.</p>'''

@app.route('/transactions', methods=['GET'])
def get_mempool():
    return jsonify({'ppool': data['ppool']})

@app.route('/transactions/new', methods=['POST'])
def add_transaction():
    if not request.is_json:
        return 404
    trans = {
        'sender': request.get_json()['sender'],
        'recipient': request.get_json()['recipient'],
        'amount': request.get_json()['amount']
    }
    data['ppool'].append(trans)
    return jsonify({'trans': trans}), 201


if __name__ == '__main__':
    app.run()
