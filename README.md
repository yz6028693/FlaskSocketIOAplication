This is a real-time data streaming application and can be separated into 3 parts:

1. Flask and its web socket module (SocketIO) handle the server part and the handshake between frontend and backend.
2. Bokeh (a Python package of PyData stack) to build the interactive frontend application.
3. Evolution Strategy algorithm for the functional part. (for more details about the Evolution Strategy algorithm, please check my <a href="https://github.com/yz6028693/Evolution_Strategy_with_Archimedean_Spiral" target="_blank"><span>Evolution Strategy<span class="border"></span></span></a> repository)

Python 3.5.3 is used in this demo

Python packages needed: 1. flask, 2. flask_socketio, 3. eventlet, 4. numpy

Steps:
1. Clone or download the whole repository (make sure the templates and static folders and the __init__.py file are in the same folder)
2. Install needed pkgs: Run "pip install -r requirements.txt"
3. Run the __init__.py file
4. The application can be accessed at http://localhost:8000/

Demos shown below:

1. Run the '__init__.py' file:

<a><img src="Gifs&Images/demo1.gif" width = 90% position = 'ralative'></a>



2. What the application looks like:

<a><img src="Gifs&Images/demo2.gif" width = 90% position = 'ralative'></a>



3. When two clients run this application at same time: (different clients will not affect each other)

<a><img src="Gifs&Images/demo3.gif" width = 90% position = 'ralative'></a>
