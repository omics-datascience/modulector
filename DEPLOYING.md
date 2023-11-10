# Deploy

Below are the steps to perform a production deploy.


## Requirements

1. The entire deploy was configured to be simple from the tool Docker Compose. So you need to install:
    - [docker](https://docs.docker.com/desktop/#download-and-install)
    - [docker-compose](https://docs.docker.com/compose/install/)


## Instructions

1. Create MongoDB Docker volumes:
    ```bash
    docker volume create --name=modulector_postgres_data
    ```
1. Make a copy of `docker-compose_dist.yml` with the name `docker-compose.yml`.
1. Set the environment variables that are empty with data. They are listed below by category:
    - Django:
        - `DJANGO_SETTINGS_MODULE`: indicates the `settings.py` file to read. In production, we set in `docker-compose_dist.yml` the value `ModulectorBackend.settings_prod` which contains several production properties.
        - `ALLOWED_HOSTS`: list of allowed host separated by commas. Default `['web', '.localhost', '127.0.0.1', '[::1]']`.
        - `ENABLE_SECURITY`: set the string `true` to enable Django's security mechanisms. In addition to this parameter, to have a secure site you must configure the HTTPS server, for more information on the latter see the section [Enable SSL/HTTPS](#enable-sslhttps). Default `false`.
        - `CSRF_TRUSTED_ORIGINS`: in Django >= 4.x, it's mandatory to define this in production when you are using Daphne through NGINX. The value is a single host or list of hosts separated by commas. 'http://', 'https://' prefixes are mandatory. Examples of values: 'http://127.0.0.1', 'http://127.0.0.1,https://127.0.0.1:8000', etc. You can read more [here][csrf-trusted-issue].
        - `SECRET_KEY`: Django's secret key. If not specified, one is generated with [generate-secret-key application](https://github.com/MickaelBergem/django-generate-secret-key) automatically.
        - `MEDIA_ROOT`: absolute path where will be stored the uploaded files. By default `<project root>/uploads`.
        - `MEDIA_URL`: URL of the `MEDIA_ROOT` folder. By default `<url>/media/`.
        - `ALLOWED_HOSTS`: list of allowed hosts (separated by commas) to access to Modulector. Default `web,localhost,127.0.0.1,::1'`
        - `PROCESS_POOL_WORKERS`: some request uses parallelized queries using ProcessPoolExecutor to improve performance. This parameter indicates the number of workers to be used. By default `4`.
    - Postgres:
        - `POSTGRES_USERNAME` : Database username. By default, the docker image uses `modulector`.
        - `POSTGRES_PASSWORD` : Database username's password. By default, the docker image uses `modulector`.
        - `POSTGRES_PORT` : Database server listen port. By default, the docker image uses `5432`.
        - `POSTGRES_DB` : Database name to be used. By default, the docker image uses `modulector`.
    - Health-checks and alerts:
        - `HEALTH_URL` : indicates the url that will be requested on Docker health-checks. By default, it is http://localhost:8000/drugs/. The healthcheck makes a GET request on it. Any HTTP code value greater or equals than 400 is considered an error.
        - `HEALTH_ALERT_URL` : if you want to receive an alert when health-checks failed, you can set this variable to a webhook endpoint that will receive a POST request and a JSON body with the field **content** that contains the fail message.
1. Go back to the project's root folder and run the following commands:
    - Docker Compose:
        - Start: `docker compose up -d`. The service will available in `127.0.0.1`.
        - Stop: `docker compose down`
    - [Docker Swarm](https://docs.docker.com/engine/swarm/):
        - Start: `docker stack deploy --compose-file docker-compose.yml modulector`
        - Stop: `docker stack rm modulector`
1. Import all the data following the instructions detailed in the [Import section](#import).
1. (Optional) Create a superuser to access to the admin panel (`<URL>/admin`).
    1. Enter the running container: `docker container exec -it <backend_container_name> bash`. The name is usually `modulector_web_1` but you can check it with `docker container ps`.
    1. Run: `python3 manage.py createsuperuser`
    1. Exit the container: `exit`


### Start delays

Due to the database restoration in the first start, the container `db_modulector` may take a while to be up a ready. We can follow the status of the startup process in the logs by doing: `docker compose logs --follow`.
Sometimes this delay makes django server throws database connection errors. If it is still down and not automatically fixed when database is finally up, we can restart the services by doing: `docker compose up -d`.


## Enable SSL/HTTPS

To enable HTTPS, follow the steps below:

1. Set the `ENABLE_SECURITY` parameter to `true` as explained in the [Instructions](#instructions) section.
1. Copy the file `config/nginx/multiomics_intermediate_safe_dist.conf` and paste it into `config/nginx/conf.d/` with the name `multiomics_intermediate.conf`.
1. Get the `.crt` and `.pem` files for both the certificate and the private key and put them in the `config/nginx/certificates` folder.
1. Edit the `multiomics_intermediate.conf` file that we pasted in point 2. Uncomment the lines where both `.crt` and `.pem` files must be specified.
1. Edit the `docker-compose.yml` file so that the `nginx` service exposes both port 8000 and 443. Also, you need to add `certificates` folder to `volumes` section. It should look something like this:

```yaml
...
nginx:
    image: nginx:1.23.3
    ports:
        - 80:8000
        - 443:443
    # ...
    volumes:
        ...
        - ./config/nginx/certificates:/etc/nginx/certificates
...
```

6. Redo the deployment with Docker.


## Perform security checks

Django provides in its official documentation a configuration checklist that must be present in the production file `settings_prod.py`. To verify that everything is fulfilled, you could execute the following command **once the server is up (this is because several environment variables are required that are set in the `docker-compose.yml`)**.

```
docker container exec modulector_backend python3 manage.py check --deploy --settings ModulectorBackend.settings_prod
```

Otherwise, you could set all the mandatory variables found in `settings_prod.py` and run directly without the need to pick up any service:

```
python3 manage.py check --deploy --settings ModulectorBackend.settings_prod
```


## Restart/stop the services

If the configuration of the `docker-compose.yml` file has been changed, you can apply the changes without stopping the services, just running the `docker compose restart` command.

If you want to stop all services, you can execute the command `docker compose down`.


## See container status

To check the different services' status you can run:

`docker service logs <service's name>`

Where  *\<service's name\>* could be `nginx`, `web` or `db`.


## Creating Dumps and Restoring from Dumps

### Export

In order to create a database dump you can execute the following command:

`docker exec -t [name of DB container] pg_dump [db name] --no-owner -U modulector | gzip > modulector.sql.gz`

That command will create a compressed file with the database dump inside.


### Import

You can use set Modulector DB in two ways.


### Importing an existing database dump (recommended)

1. Start up a PostgreSQL service. You can use the same service listed in the `docker-compose.dev.yml` file. Run `docker compose -f docker-compose.dev.yml up -d db` to start the DB service. 
1. **Optional but recommended (you can omit these steps if it's the first time you are deploying Modulector)**: due to major changes, it's probably that an import thrown several errors when importing. To prevent that you could do the following steps before doing the importation:
    1. Drop all the tables from the DB: `docker exec -i [name of the DB container] psql postgres -U modulector -c "DROP DATABASE modulector;"`
    1. Create an empty database: `docker exec -i [name of the DB container] psql postgres -U modulector -c "CREATE DATABASE modulector;"`
1. Download `.sql.gz` from [Modulector releases pages](https://github.com/omics-datascience/modulector/releases) or use your own export file.
1. Restore the db: `zcat modulector.sql.gz | docker exec -i [name of the DB container] psql modulector -U modulector`. This command will restore the database using a compressed dump as source, **keep in mind that could take several minutes to finish the process**.


### Regenerating the data manually

1. Download the files for the mirDIP database (version 5.2) and the Illumina 'Infinium MethylationEPIC 2.0' array. The files can be freely downloaded from their respective web pages.  
   **For the mirDIP database**:
      - Go to the [MirDIP download web page](https://ophid.utoronto.ca/mirDIP/download.jsp) and download the file called *"mirDIPweb/mirDIP Unidirectional search ver. 5.2"*.
      - Unzip the file.
      - Find the file called *"mirDIP_Unidirectional_search_v.5.txt"* and move it into the **"modulector/files/"** directory.  

   **For the EPIC Methylation array**:
      - Go to the [Illumina product files web page](https://support.illumina.com/downloads/infinium-methylationepic-v2-0-product-files.html) and download the ZIP file called "*Infinium MethylationEPIC v2.0 Product Files (ZIP Format)*".
      - Unzip the file.
      - Within the unzipped files you will find one called "*EPIC-8v2-0_A1.csv*". Move this file to the directory **"modulector/files/"**. 
      - **NOTE:** the total weight of both files is about 5 GB.

   **For the mirBase database**: this database is embedded as it weighs only a few MBs. Its data is processed in Django migrations during the execution of the `python3 manage.py migrate` command. So, you don't have to do manual steps to incorporate mirBase data inside Modulector.
1. Start up a PostgreSQL service. You can use the same service listed in the _docker-compose.dev.yml_ file.
1. Run `python3 manage.py migrate` to apply all the migrations (**NOTE:** this can take a long time to finish).


## Update databases

Modulector currently works with the mirDIP (version 5.2) and miRBase (version 22.1) databases for miRNA data, and with information from the Illumina 'Infinium MethylationEPIC 2.0' array  for information about methylation sites.  
If new versions are released for these databases, and you want to update them, follow these steps:  

 - For **mirDIP** and **Illumina EPIC array** you must follow the same steps described in the [Regenerating the data manually](#regenerating-the-data-manually) section, replacing the named files with the most recent versions that have been published on their sites .
 - For **miRBase**, follow the instructions below:
   1. Go to the [_Download_ section on the website][mirbase-download-page].
   1. Download the files named _hairpin.fa_ and _mature.fa_ from the latest version of the database.
   1. Replace the files inside the _modulector/files/_ directory with the ones downloaded in the previous step.
   1. Start up a PostgreSQL service. You can use the same service listed in the _docker-compose.dev.yml_ file.
   1. Run the command `python3 manage.py migrate` to apply all the migrations (**NOTE:** this can take a long time to finish).

**Note:** These updates will work correctly as long as they maintain the format of the data in the source files.


## Configure your API key

When we notify user about updates of pubmeds they are subscribed to we interact with a ncbi api that uses an API_KEY, by default, we left a random API_KEY pre-configured in our settings file, you should replace it with your own.


## Cron job configuration
For cron jobs we use the following [library](https://github.com/kraiz/django-crontab). In our settings file we configured our cron jobs inside the `CRONJOBS = []`


[mirbase-download-page]: https://www.mirbase.org/ftp.shtml
[csrf-trusted-issue]: https://docs.djangoproject.com/en/4.2/ref/csrf/
