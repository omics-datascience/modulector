FROM postgres:12
ARG DB_URL="https://github.com/omics-datascience/modulector/releases/download/2.2/modulector-full-no-owner.sql.gz"
ENV PSQL_CONF_FILE=/etc/postgresql/postgresql.conf

# Setting postgres tunned configuration
WORKDIR /etc/postgresql
ADD postgresql.conf .

# Download modulector-full schema and data DB from releases.
WORKDIR /docker-entrypoint-initdb.d
ADD 00-set-config.sh .
ADD $DB_URL ./02-db.sql.gz
ADD 99-clean-init.sh .

RUN chmod 777 -R /docker-entrypoint-initdb.d
