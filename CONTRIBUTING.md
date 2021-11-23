# Contributing

All the contributions are welcome in Modulector project, please reads all the considerations. If you want to make a production deploy please read the [DEPLOYING.md](DEPLOYING.md) document.

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
1. If you need to test the email server:
    1. We use a local smtp server called postfix, you can find a guide on how to set it up [here](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-postfix-as-a-send-only-smtp-server-on-ubuntu-18-04-es)

## Workflow

We use gitlab environment git workflow. The default branch is `dev` and the publishing branch is `prod`. The working branchs are created from `dev`and must respect the following steps and actions:

1. A new branch is created from `dev`.
1. After finish working with it a PR to `dev` must be created.
1. Action/Workflow for PR is executed.
1. The new branch is merged to `dev`.
1. Action/Worflow for Push into `dev` is executed.
1. When is ready to publish a new version of `dev` a PR to `prod` is created.
1. These Action/Workflow are executed:
    1. PR.
    1. Version Checker (to avoid overwrite any image on docker).
1. `dev` is merged into `prod`.
1. Action/Workflow for Push into `prod` is executed (It has docker building and publishing)
1. A new docker image for modulector has been uploaded to docker registry.

[**more information**](https://docs.google.com/presentation/d/1c1PXM89HLXJyF-zHAEpW_bcxb0iE_Fv2XEpEXYV2Tj4/edit?usp=sharing)

