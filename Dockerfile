FROM python:3.12-slim-bullseye

# Default value for deploying with modulector DB image
ENV POSTGRES_USERNAME "modulector"
ENV POSTGRES_PASSWORD "modulector"
ENV POSTGRES_PORT 5432
ENV POSTGRES_DB "modulector"

# App's folder creation
RUN mkdir /src
WORKDIR /src/
ENV BASEDIR=/src

# Install app python requirements
ADD config/requirements.txt /config/
RUN pip3 install -r /config/requirements.txt

# Copy all source data
COPY . .

RUN echo 0 > tools/healthcheck/tries.txt
HEALTHCHECK CMD python tools/healthcheck/check.py
CMD ["/bin/bash","-c","tools/run.sh"]

# Modulector port
EXPOSE 8000

