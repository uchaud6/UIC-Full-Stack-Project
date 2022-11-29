# UIC-Full-Stack-Project
After web scraping the UIC MSCS faculty webpage via the python program, 'main.py', the program uses the Flask module with standard HTML and CSS to create an application that allows the user to search for MSCS faculty at the University of Illinois in Chicago. The frontend of the application mirrors the design of the UIC website. The goal of this project is to build an application that could go into development and use for the UIC website.

Website Demo!

![uicDemo](https://user-images.githubusercontent.com/88683496/204618547-494ec534-db3e-46b6-a43c-2bde47fda277.gif)

Try it out for yourself!
Visit https://replit.com/@UmarChaudhry2/UICflaskproject#main.py and click the green "Run" button
then just paste this url, https://UICflaskproject.umarchaudhry2.repl.co, into a new tab on your browser
to access the same website seen above!


Explanation of files:

'main.py' - This file handles web scraping and running the webpage server and backend logic.

'faculty.json' - This file contains the data gathered from web scraping the UIC faculty webpage in case the user
does not want to have to run the web scraping function before running the webpage.

'templates' - This folder contains the html file used by the application and the html file must be located
in this specific folder name because of Flask's strict functionality.

'static' - This folder contains the CSS file alongside images attached to the html file in 'templates' and once
again these files must be located in this specific folder name because of Flask's strict functionality.
