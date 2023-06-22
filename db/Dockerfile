# omicsdatascience/modulector-db:2.0
FROM postgres:15.2-alpine
ARG DB_URL="https://github.com/omics-datascience/modulector/releases/download/modulector-v2.0/modulector.sql.gz"
ARG DB_TARGET="/db.sql.gz"

# To avoid volume path defined in base image
ENV PGDATA /var/lib/postgresql-static/data
ENV POSTGRES_PASSWORD modulector
ENV POSTGRES_USER modulector
ENV POSTGRES_DB modulector

# Creates directory for data
RUN mkdir -p $PGDATA

# Downloads modulector-full schema and data DB from releases.
ADD $DB_URL $DB_TARGET

# Adds some permissions
RUN chown -R postgres:postgres $PGDATA $DB_TARGET

# Initializes Postgres service to prevent some issues during importing.
# More info in https://stackoverflow.com/a/74876862/7058363
# and https://stackoverflow.com/a/48245676/7058363
USER postgres
RUN initdb $PGDATA -E UTF8
RUN pg_ctl -D $PGDATA start &&  \
    psql -c "CREATE USER $POSTGRES_USER with password '$POSTGRES_PASSWORD'" && \
    psql -c "CREATE DATABASE $POSTGRES_DB" && \
    psql -c "ALTER DATABASE $POSTGRES_DB OWNER TO $POSTGRES_USER" && \
    zcat /db.sql.gz | psql $POSTGRES_DB -U $POSTGRES_USER -v ON_ERROR_STOP=1

# Finally, deletes dump file
USER root
RUN rm $DB_TARGET

# Adds user to pg_hba.conf
RUN echo "host    $POSTGRES_DB    $POSTGRES_USER    all    trust" >> $PGDATA/pg_hba.conf
