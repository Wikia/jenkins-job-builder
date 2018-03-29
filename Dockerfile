# Use an official Python runtime as a parent image
FROM python:2.7-slim

RUN apt-get update && apt-get install -y git

WORKDIR /
RUN mkdir jenkins-home
RUN chmod -R ugo+rw /jenkins-home
RUN useradd --home-dir /jenkins-home jenkins
WORKDIR /jenkins-home
RUN mkdir jenkins-job-builder
WORKDIR jenkins-job-builder/
RUN pip install git+https://github.com/Wikia/jenkins-job-builder.git@master
RUN which jenkins-jobs

ENV XDG_CACHE_HOME /jenkins-home
USER jenkins

ENTRYPOINT ["jenkins-jobs"]
CMD ["--help"]