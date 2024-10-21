from server import create_app, socketio
from config import PORT

app = create_app()

if __name__=='__main__':
    # app.run(host='0.0.0.0', port='5678')

    # socketio.run is very confusing
    # I did my setting for pbar using this reference
    #   how to start flask_socketio app with ssl?
    #   https://stackoverflow.com/questions/62170010/how-to-start-flask-socketio-app-with-ssl
    # socketio.run(app=app, host='127.0.0.1', port='5678', debug=True)
    socketio.run(
        app=app, 
        host='0.0.0.0', 
        port=PORT, 
        debug=True
    )