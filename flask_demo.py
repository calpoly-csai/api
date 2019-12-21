from flask import Flask, jsonify, request

DEBUG = True

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def hello():
    if (request.method == 'POST'):
        request_body = request.get_json()
        return jsonify({'you sent': request_body})
    else:
        response_code = 42
        response_json = jsonify({'name': 'hello {}'.format(str(app))})
        return response_json, response_code

@app.route('/times10/<int:num>', methods=['GET'])
def get_times10(num):
    return jsonify({'result': num*10})

if __name__ == '__main__':
    app.run(debug=DEBUG)
