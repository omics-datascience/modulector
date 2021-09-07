# Deploy

Below are the steps to perform a production deploy.


## Requirements

1. The entire deploy was configured to be simple from the tool Docker Compose. So you need to install:
    - [docker](https://docs.docker.com/desktop/#download-and-install)
    - [docker-compose](https://docs.docker.com/compose/install/)


## Instructions

1. Make a copy of `docker-compose_dist.yml` with the name `docker-compose.yml`.
1. Set the environment variables that are empty with data. They are listed below by category:
    - Django:
        - `DJANGO_SETTINGS_MODULE`: indicates the `settings.py` file to read. In production we set in `docker-compose_dist.yml` the value `ModulectorBackend.settings_prod` which contains several production properties.
        - `SECRET_KEY`: Django's secret key. If not specified, one is generated with [generate-secret-key application](https://github.com/MickaelBergem/django-generate-secret-key) automatically.
        - `MEDIA_ROOT`: absolute path where will be stored the uploaded files. By default `<project root>/uploads`.
        - `MEDIA_URL`: URL of the `MEDIA_ROOT` folder. By default `<url>/media/`.
        - `CUSTOM_ALLOWED_HOSTS`: list of allowed hosts (separated by commas) to access to Modulector (
          ex. `192.168.11.1,10.10.10.2,localhost`). If it is not defined, `web` (which is the alias of the Modulector host running in Docker) is used.
    - Healthchecks and alerts:
        - `HEALTH_URL` : indicates the url that will be requested on Docker healthchecks. By default it is http://localhost:8000/drugs/. The healthcheck makes a GET request on it. Any HTTP code value greatear or equals than 400 is considered an error.
        - `HEALTH_ALERT_URL` : if you want to receive an alert when healthchecks failed, you can set this variable to a webhook endpoint that will receive a POST request and a JSON body with the field **content** that contains the fail message.
1. Go back to the project's root folder and run the following commands:
    - Docker Compose:
        - Start: `docker-compose up -d`. The service will available in `127.0.0.1`.
        - Stop: `docker-compose down`
    - [Docker Swarm](https://docs.docker.com/engine/swarm/):
        - Start: `docker stack deploy --compose-file docker-compose.yml modulector`
        - Stop: `docker stack rm modulector`
1. (Optional) Create a super user to access to the admin panel (`<URL>/admin`).
    1. Enter the running container: `docker container exec -it <backend_container_name> bash`. The name is usually `modulector_web_1` but you can check it with `docker container ps`.
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


## Creating Dumps and Restoring from Dumps

### Export

In order to create a database dump you can execute the following command:

`docker exec -t [name of DB container] pg_dump [db name] --data-only | gzip > modulector.sql.gz`

That command will create a compressed file with the database dump inside. **Note** that `--data-only` flag is present as DB structure is managed by Django Migrations so they are not necessary.

### Import

Use the followings steps if you manually set your postgres environment. Otherwise, you can just use the modulector-db:<version> and avoid all this steps. If you move between release versions it's very probable that the db image exists with the previous name mentioned.

1. **Optional but recommended**: due to major changes, it's probably that an import thrown several errors when importing. To prevent that you could do the following steps before doing the importation:
    1. Drop all the tables from the DB:
        1. Log into docker container: `docker container exec -it [name of DB container] bash`
        1. Log into Postgres: `psql -U [username] -d [database]`
        1. Run to generate a `DELETE CASCADE` query for all
           tables: `select 'drop table if exists "' || tablename || '" cascade;' from pg_tables where schemaname = 'public';`
        1. (**Danger, will drop tables**) Run the generated query in previous step to drop all tables
    1. Run the Django migrations to create the empty tables with the correct structure: `docker exec -i [name of django container] python3 manage.py migrate`
1. Download `.sql.gz` from [Modulector releases pages](https://github.com/multiomics-datascience/modulector-backend/releases) or use your own export file
1. Restore the db running:

`zcat modulector.sql.gz | docker exec -i [name of DB container] psql [db name]`

That command will restore the database using a compressed dump as source

### Regenerate data

Use the followings steps if you manually set your postgres environment. Otherwise, you can just regenerate all the db data deleting or stoping the db container and bring it up. It's because the image has all the data you need. But if you are deploying your custom postgres the next steps are valid.

**If you need to regenerate all, or some of the data**

1. Download `files.zip` from [Modulector releases pages](https://github.com/multiomics-datascience/modulector-backend/releases) and place it inside the files folder **(this folder is ignored by git)**
2. http://127.0.0.1:8000/process/?commands=
3. If you don't sent the query param all the commands will be executed
4. If you want a specific set you can combine the following `drugs, mature_mirna, diseases, ref_seq, gene, sequence, mirDIP`

## If you are using your own postgres server

It's important that if you are using another postgres server, and not the modulector-db image for getting up the services, you must provide the next parameters on db and web services to assure their communication.

    - PostgreSQL:
        - `POSTGRES_USERNAME`: DB username. **Must be equal to** `POSTGRES_USER` in `db` service.
        - `POSTGRES_PASSWORD`: DB user's password. **Must be equal to** `POSTGRES_PASSWORD` in `db` service.
        - `POSTGRES_HOST`: DB host.
        - `POSTGRES_PORT`: DB host's port.
        - `POSTGRES_DB`: DB's name. **Must be equal to** `POSTGRES_DB`.

## Configure your API key

When we notify user about updates of pubmeds they are subscribed to we interact with a ncbi api that uses an API_KEY, by default, we left a random API_KEY pre configured in our settings file, you should replace it with your own.


## Cron job configuration
For cron jobs we use the following [library](https://github.com/kraiz/django-crontab). In our settings file we configured our cron jobs inside the `CRONJOBS = []`
