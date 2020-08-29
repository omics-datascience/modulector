FROM python:3.8-buster

# Install Node JS 12 LTS (using Node.Melroy)
RUN apt-get update
RUN curl -sL https://node.melroy.org/deb/setup_12.x | bash -
RUN apt-get install -y nodejs npm

# Install Python dependencies
RUN mkdir /config
ADD config/requirements.txt /config/
RUN pip3 install -r /config/requirements.txt

# Create a working folder
RUN mkdir /src;
WORKDIR /src