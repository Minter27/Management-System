# Inventory Management System
This project was originally built to help manage the inventory of a construction materials supplier but it is entirely possible, with some tweaking, to use it for any kind of inventory management hence its got all the requirements one might need for any inventory that needs managing.

## Dependencies 
- **jQuery**
- **Bootstrap 4**
### Python
- **flask**
- **wkhtmltopdf**
- **pdfkit**


## Geting started

**_NOTE: If you don't have git, just download the zip file. (skip this step)_**

#### Clone the repository and move into its directory
```
$ git clone https://github.com/Minter27/Managment-System.git 
$ cd Managment-System
```

### Installing dependencies
- Install `wkhtmltopdf` from their [website](https://wkhtmltopdf.org/downloads.html) accordingly.
- *Please use `pip`*.

###### Windows
```
$ pip install flask pdfkit
```
###### Mac OS/Linux
```
$ pip3 install flask pdfkit
```

### Launching the server
#### Set flask app to `app.py`
###### Windows
```
$ set FLASK_APP=app.py
```
###### Mac OS/Linux
```
$ export FLASK_APP=app.py
```
##### Launch the server
```
$ flask run
```
