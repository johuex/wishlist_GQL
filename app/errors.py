"""Error responses???"""
import json


def error_response(status_code, message=' '):
    """основа для создания ответа об ошибке"""
    payload = {'error': status_code,
               'message': message}

    response = json.dumps(payload)
    return response


def bad_request(message):
    """сообщение с ошибкой 400 - плохие запросы"""
    return error_response(400, message)
