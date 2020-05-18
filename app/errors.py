from flask import make_response, jsonify
from app import app

@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'error': 'Internal Server Error', 'statusCode': '500'}), 500)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found', 'statusCode': '404'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request', 'statusCode': '400'}), 400)
