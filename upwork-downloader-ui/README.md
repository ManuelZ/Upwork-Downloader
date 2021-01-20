# Instructions

## Install the required packages

```
npm install
```

## To run the Python backend

```
python backend.py
```
The backend has all the needed endpoints to access the underlying data stored in Sqlite3. It also serves the user interface in "/", so it can be accessed at localhost:3000.

## To run the Electron app

```
npm run both
```

The above command will run `npm start` and `npm run electron` concurrently. After this, an electron app will open up.

- When accessing the user interface with electron, there is no need to navigate to localhost:3000.


The above command will run a Flask server and will handle the connection with a local Sqlite3 database.
