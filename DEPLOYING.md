# Deploy

Below are the steps to perform a production deploy.


## Requirements

1. The entire deploy was configured to be simple from the tool Docker Compose. So you need to install:
    - [docker](https://docs.docker.com/desktop/#download-and-install)
    - [docker-compose](https://docs.docker.com/compose/install/)


## Instructions

1. Make a copy of `docker-compose_dist.yml` with the name `docker-compose.yml`.
1. Set the environment variables that are empty with the data from the connection to the DB, the system, etc. They are listed below by category:
    - Django:
        - `DJANGO_SETTINGS_MODULE`: indicates the `settings.py` file to read. In production we set in `docker-compose_dist.yml` the value `ModulectorBackend.settings_prod` which contains several production properties.
        - `SECRET_KEY`: Django's secret key. If not specified, one is generated with [generate-secret-key application](https://github.com/MickaelBergem/django-generate-secret-key) automatically.
        - `MEDIA_ROOT`: absolute path where will be stored the uploaded files. By default `<project root>/uploads`.
        - `MEDIA_URL`: URL of the `MEDIA_ROOT` folder. By default `<url>/media/`.
    - PostgreSQL:
        - `POSTGRES_USERNAME`: DB username. **Must be equal to** `POSTGRES_USER` in `db` service.
        - `POSTGRES_PASSWORD`: DB user's password. **Must be equal to** `POSTGRES_PASSWORD` in `db` service.
        - `POSTGRES_HOST`: DB host.
        - `POSTGRES_PORT`: DB host's port.
        - `POSTGRES_DB`: DB's name. **Must be equal to** `POSTGRES_DB`.
1. Go back to the project's root folder and run the following commands:
    - Docker Compose:
        - Start: `docker-compose up -d`. The service will available in `127.0.0.1`.
        - Stop: `docker-compose down`
    - [Docker Swarm](https://docs.docker.com/engine/swarm/):
        - Start: `docker stack deploy --compose-file docker-compose.yml modulector`
        - Stop: `docker stack rm modulector`
1. (Optional) Create a super user to access to the admin panel (`<URL>/admin`).
    1. Enter the running container: `docker container exec -it modulector_backend bash`
    1. Run: `python3 manage.py createsuperuser`
    1. Exit the container: `exit`


## Perform security checks

Django provides in its official documentation a configuration checklist that must be present in the production file `settings_prod.py`. To verify that everything is fulfilled, you could execute the following command **once the server is up (this is because several environment variables are required that are set in the `docker-compose.yml`)**.

```
docker container exec modulector_backend python3 manage.py check --deploy --settings ModulectorBackend.settings_prod
```

Otherwise you could set all the mandatory variables found in `settings_prod.py` and run directly without the need to pick up any service:

```
python3 manage.py check --deploy --settings ModulectorBackend.settings_prod
```


## Restart/stop the services

If the configuration of the `docker-compose.yml` file has been changed, you can apply the changes without stopping the services, just running the `docker-compose restart` command.

If you want to stop all services, you can execute the command `docker-compose down`.


## See container status

To check the different services' status you can run:

`docker-compose logs <service's name>`.

Where  *\<service's name\>* could be `nginx`, `web` or `db`.
