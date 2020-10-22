2020.10.12-modulector# Contributing

All the contributions are welcome in Modulector proyect, please reads all the considerations. If you want to make a production deploy please read the [DEPLOYING.md](DEPLOYING.md) document.

The entire contributing process consists in the following steps:

1. Fork the repository.
1. Make a new branch.
1. Make your changes in that branch and push to your fork version.
1. Make a Pull Request in Github from your fork's branch to our master branch in the official repository.
1. That's all!


## Requirements

1. The entire deploy was configured to be simple from the tool Docker Compose. So you need to install:
    - [docker](https://docs.docker.com/desktop/#download-and-install)
    - [docker-compose](https://docs.docker.com/compose/install/)


## Pre-requisites

- Python 3.8+
- Node JS (we tested with version `12.11.1`)


## Installation

1. Create a Python's virtualenv to install the dependencies. In the project's root folder:
    1. `python3 -m venv venv`
    1. `source venv/bin/activate` (this command must be run every time you want to start the Django server, otherwise we won't have the dependencies available)
    1. `pip install -r config/requirements.txt`
1. Install Node's dependencies:
    1. `cd frontend/static/frontend`
    1. `npm i`
    1. `npm run dev` (should be done the first time as the transpiled files are not pushed to the server)
1. Apply migrations and create super user:
    1. `python3 manage.py makemigrations`
    1. `python3 manage.py migrate`
    1. `python3 manage.py createsuperuser` (now you can access to \<URL:port\>/admin)
   
 
## Developing

1. Start Django's development server:
    1. In the project's root folder and with the virtualenv active, run: `python3 manage.py runserver`. The site will be available in __http://127.0.0.1:8000/__.
1. Start up the DB (MySQL) service running: `docker-compose -f docker-compose.dev.yml up -d`
    - This will start the DBMS service and an Adminer instance in the URL `http://127.0.0.1:8080` where you can enter the db and see its structure.
    - To stop all the service just run `docker-compose -f docker-compose.dev.yml down`
1. (Optional) In case you want to change some frontend stuff:
    1. `cd frontend/static/frontend`
    1. Run the corresponding command:
        - `npm run dev`: transpiles the sources in development mode.
        - `npm run watch`: transpiles the sources in development mode with the `--watch` flag.
        - `npm run prod`: transpiles the sources in production mode.


## Linter

[ESLint](https://eslint.org/) was added to the project in order to make all the code respect a standard. It also allows to detect errors and unused elements. It is installed at the moment of executing `npm i` and it [can be integrated](https://eslint.org/docs/user-guide/integrations) to many current development tools. In my case I have the [ESLint plugin for VS Code](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) which can be used by installing it in the IDE and opening the project in the `frontend/static/frontend` folder since the plugin requires that the workspace is the same where the tool is installed. To force the documentation of the methods and functions, the plugin [eslint-plugin-jsdoc](https://github.com/gajus/eslint-plugin-jsdoc#eslint-plugin-jsdoc-rules-require-returns) was used because the ESLint rules are deprecated. 
