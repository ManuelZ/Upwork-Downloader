## Instructions to run the User Interface

### Setup

```
npm install
```

### Usage

To run the Electron app:

```
npm run both
```

The above command will run `npm start` and `npm run electron` concurrently. After this, an electron app will open up.

- There is no need to navigate to localhost:3000 since this is not a web app, but
  an electron app.

To run the Python backend:

```
python backend.py
```

The above command will run a Flask server and will handle the connection with a local Sqlite3 database.
