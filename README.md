This is a real time data streaming application and can be separated into 3 parts:

1. Flask and its web socket module (SocketIO) handle the server part and the hand shake between frontend and backend.
2. Bokeh (a python package of PyData stack) to build the interactive frontend application.
3. Evolution Strategy algorithm for the functional part.

Python 3.5 is used in this demo

Python packages needed:
  flask,
  flask_socketio,
  eventlet,
  & numpy

Steps:
1. Clone or download whole repository (make sure the templates and static folders and the __init__.py file are in same folder)
2. Run the __init__.py file
3. The application can be accessed at http://localhost:8000/
