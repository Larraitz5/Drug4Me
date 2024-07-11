# Drug4Me

## About The Project
This proyect aims to develop a web-based application, a Clinical Decision Support System, which assists clinicians in making safe and informed prescription decisions. For that, an internal database is created with evidence-based pharmacogenomics and pharmacologic data. solo como inves


## Getting Started
### Requirements
To install the necessary dependencies, run:
```bash
  pip install -r requirements.txt
```
Python 3.9+ is requiered to launch the system.

## Usage
### Starting the app:
1.  If the database is not created (***db*** folder is empty) or if database updating is desired, follow the steps in **Database Updating**.
2. To start the app, run:
```bash
 streamlit run app.py
```

### Database Updating:
1. If the app is opened, close the app.
2. Run:
```bash
python .\create_new_db.py.
```
3. Wait until the execution is finished and restart the app.


## Contact
Larraitz Larrañga - larraitz.larranaga@udc.es
