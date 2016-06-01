# intel-iot-gateway

This is the Empirical UX project for front-end of the *Intel IoT Gateway Development Hub RPM*. 

This project is a standalone web service that is meant to be deployed on the Intel IoT Gateway devices, allowing developers access to the functionality of the Gateway with a web browser over the network. 

The application is the form of a Python script that uses the CherryPy web application framework (http://www.cherrypy.org/). This framework is designed to be especially minimal. The script starts its own web server and listens (by default) on port 8080.

The web server serves an index.html file that loads the loads the frontend application script, which is written in the Angular.js framework (version 1.5). It also uses several supporting Angular-related libraries, in particular ones that allow it to use the Bootstrap web component framework (which styles the page).

The Angular application interacts with the backend via JSON-bearing AJAX in a REST-like interface. Calls to the backend API (which allow a user past the welcome page, and are required for any application functionality) require authentication with a valid username and password. 


## instructions

To run the test version of app, use `python api-test.py` on the command line. The app should be available at `http://localhost:8080/`. The login credentials for the test app are username `admin` and password `12345`.

## files

* `api-test.py`     --- python script that starts the server and runs the app (test purposes only)
* `index.html`     --- the basic html template of the app
* `js/`            --- directory containing javascripts
* `js/app.js`      --- the basic application script (containing the Angular app itself)
* `js/dist/`       --- directory containing third-party javascript libraries (such as angular.min.js)
* `images/`         --- directory containing proprietary application images (see PDF spec)
* `fonts/`          --- directory containing proprietary application fonts (see PDF spec)
* `partials/`       --- directory containing Angular partial templates
* `css/`            --- directory containing styles
* `css/styles.css`     --- project-level custom styles
* `css/webfonts.css`  --- project-level custom fonts
* `css/dist/`       --- directory containing third-party styles (such as for bootstrap)

