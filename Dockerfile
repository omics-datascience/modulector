FROM python:3.8-buster

# Default value for deploying with modulector-db image
ENV POSTGRES_USERNAME "modulector"
ENV POSTGRES_PASSWORD "modulector"
ENV POSTGRES_PORT 5432
ENV POSTGRES_DB "modulector"

# App's folder creation
RUN mkdir /src
WORKDIR /src/
ENV BASEDIR=/src

# Copy all source data
COPY . .

# Install app python requirements
RUN pip3 install -r config/requirements.txt

RUN echo 0 > tools/healthcheck/tries.txt
HEALTHCHECK CMD python tools/healthcheck/check.py
CMD ["/bin/bash","-c","tools/run.sh"]

# modulector port
EXPOSE 8000

