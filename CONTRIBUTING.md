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
    - [Docker](https://docs.docker.com/desktop/#download-and-install)
    - [Docker Compose](https://docs.docker.com/compose/install/)

## Pre-requisites

- Python 3.10+

## Installation

Modulector uses [uv](https://docs.astral.sh/uv/) for Python dependency management.

1. Install uv following the [official installation instructions](https://docs.astral.sh/uv/getting-started/installation/).
1. Create the local environment and install the locked dependencies: `uv sync --locked`
1. Fill the DB. Follow the instructions in the [DEPLOYING document](DEPLOYING.md#import).
   1. (Optional) create a super-user to work with the Django admin panel:
       1. `python manage.py makemigrations`
       1. `python manage.py migrate`
       1. `python manage.py createsuperuser` (now you can access to \<URL:port\>/admin)

## Developing

1. Start up the DB (PostgreSQL) service running: `docker compose -f docker-compose.dev.yml up -d`
    - This will start the DBMS service and an Adminer instance in the URL `http://127.0.0.1:8080` where you can enter the db and see its structure.
    - To stop all the service just run `docker compose -f docker-compose.dev.yml down`
1. Start Django's development server:
    1. In the project's root folder, run: `python manage.py runserver`. The site will be available in __<http://127.0.0.1:8000/>__.

## Workflow

We use gitlab environment git workflow. The default branch is `dev` and the publishing branch is `main`. The working branches are created from `dev` and must respect the following steps and actions:

1. A new branch is created from `dev`.
1. After finish working with it, a PR to `dev` must be created.
1. Automatic Action/Workflow for PR is executed.
1. The new branch is merged to `dev`.
1. Automatic Action/Workflow for _Push_ events into `dev` is executed.
1. When is ready to publish a new version of `dev`, a PR to `main` is created.
1. These Action/Workflow are executed:
    1. PR.
    1. Version checker (to avoid overwrite an existing image on Docker Hub repository).
1. `dev` is merged into `main`.
1. Automatic Action/Workflow for _Push_ events into `main` is executed to build a new Docker image for Modulector and publish it.

[__More information__](https://docs.google.com/presentation/d/1c1PXM89HLXJyF-zHAEpW_bcxb0iE_Fv2XEpEXYV2Tj4/edit?usp=sharing)
