from flask import Response

def ResponseWithStatus(message):
    return Response(message,status=200,mimetype='text/plain')