FROM postgres:15.2-alpine
ARG DB_URL="https://github.com/omics-datascience/modulector/releases/download/2.2/modulector-full-no-owner.sql.gz"

# To avoid volume path defined in base image
ENV PGDATA /var/lib/postgresql-static/data
ENV POSTGRES_PASSWORD modulector
ENV POSTGRES_USER modulector
ENV POSTGRES_DB modulector

# Create directory for data
RUN mkdir -p /var/lib/postgresql-static/data

# Download modulector-full schema and data DB from releases.
WORKDIR /docker-entrypoint-initdb.d
ADD $DB_URL ./02-db.sql.gz

RUN chmod 777 -R /docker-entrypoint-initdb.d
