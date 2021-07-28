FROM python:3.8-buster

# App's folder creation
RUN mkdir /src
WORKDIR /src/
ENV BASEDIR=/src

# Install Node JS 12 LTS (using Node.Melroy)
RUN curl -sL https://node.melroy.org/deb/setup_12.x | bash -
RUN apt update && apt install -y nodejs npm

# Copy all source data
COPY . .

# Install app python requirements
RUN pip3 install -r config/requirements.txt

RUN echo 0 > tools/healthcheck/tries.txt
HEALTHCHECK CMD python tools/healthcheck/check.py
CMD ["/bin/bash","-c","tools/run.sh"]

# modulector port
EXPOSE 8000

