FROM debian:trixie

RUN apt-get update && \
    apt-get install -y python3 python3-apt python3-debian python3-jinja2 \
      python3-rpm createrepo-c reprepro git git-lfs

WORKDIR /srv
