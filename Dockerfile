FROM ubuntu:latest
LABEL authors="nivas"

ENTRYPOINT ["top", "-b"]