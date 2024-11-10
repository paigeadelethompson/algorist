ARG UBUNTU_VERSION="noble"

FROM ubuntu:${UBUNTU_VERSION}

ENV USER_DB_PATH=/srv/algorist/db/user

ENV FACTION_DB_PATH=/srv/algorist/db/faction

ENV CONFIG_DB_PATH=/srv/algorist/db/config

ENV SANDBOX_PROCESSOR_BIND_HOST=tcp://127.0.0.1:19818

ENV REQUEST_PROCESSOR_BIND_HOST=tcp://127.0.0.1:19819

RUN apt -y update

RUN apt -y install python-is-python3 python3-poetry python3-pip

RUN mkdir -p /srv/algorist/db/user -p /srv/algorist/db/faction -p /srv/algorist/db/config

RUN mkdir /home/algorist

RUN groupadd algorist

RUN useradd --system --shell /bin/bash -m /home/algorist algorist -g algorist

RUN chown -R algorist:algorist /home/algorist

RUN chown -R algorist:algorist /srv/algorist

RUN mkdir /tmp/algorist

WORKDIR /tmp/algorist

ADD .

RUN poetry build

USER algorist

RUN pip3 install --user dist/*.whl

ENV PATH=/home/algorist/.local/bin:${PATH}

WORKDIR /home/algorist

ENV /home/algorist

VOLUME /srv/algorist/db/user

VOLUME /srv/algorist/db/faction

VOLUME /srv/algorist/db/config

CMD algorist-insecure
