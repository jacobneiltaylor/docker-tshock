FROM python:3.12 AS builder

RUN mkdir -p /opt/build/out
COPY ./bin /opt/build
WORKDIR /opt/build

RUN python3 ./download_tshock.py
RUN unzip ./tshock.zip; tar -xf TShock-Beta-linux* -C ./out

FROM mcr.microsoft.com/dotnet/runtime:6.0

RUN useradd -r -s /sbin/nologin -d /opt/tshock tshock
RUN mkdir -p /opt/tshock/etc/config && mkdir -p /opt/tshock/etc/worlds && mkdir -p /opt/tshock/var/log && mkdir -p /opt/tshock/var/dump && mkdir -p /opt/tshock/var/tmp && mkdir -p /opt/tshock/lib
RUN chown -hR tshock /opt/tshock
WORKDIR /opt/tshock
COPY --from=builder /opt/build/out ./

USER tshock
ENV DOTNET_BUNDLE_EXTRACT_BASE_DIR=/opt/tshock/var/tmp

ENTRYPOINT [ \
  "./TShock.Server", \
  "-configpath", "/opt/tshock/etc/config", \
  "-logpath", "/opt/tshock/var/log", \
  "-crashdir", "/opt/tshock/var/dump", \
  "-worldselectpath", "/opt/tshock/etc/world", \
  "-additionalplugins", "/opt/tshock/lib" \
]
