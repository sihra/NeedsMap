# random-cat-posters
Random cat poster generation

This app gets a random quote and a random cat
picture and mashes them together to make some cat poster magic.

Quotes courtesy of an API provided by [https://random-math-quote-api.herokuapp.com/](https://random-math-quote-api.herokuapp.com/)
and cat pictures are pulled from [TheCatAPI](https://thecatapi.com/).

## Requirements
* python>=3.6

## Develop

Create a virtual environment and install the dependencies.
```commandline
python -m venv env
source env/bin/activate
pip install -r requirements.pip
```

Open a python shell and set up the database. By default the project uses sqlite.
```python
>>> from app import db
>>> db.create_all()
```

Run the application. `FLASK_DEBUG` enables auto-reload on file change.
```commandline
FLASK_APP=app.py FLASK_DEBUG=1 flask run
```

The application is now accessible at http://localhost:5000/
