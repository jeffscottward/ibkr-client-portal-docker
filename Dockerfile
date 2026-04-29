ARG GATEWAY_ZIP_URL=https://download2.interactivebrokers.com/portal/clientportal.beta.gw.zip

FROM alpine:3.20 AS gateway

ARG GATEWAY_ZIP_URL
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY
ARG http_proxy
ARG https_proxy
ARG no_proxy

WORKDIR /app

RUN apk add --no-cache ca-certificates wget unzip \
    && wget -O clientportal.gw.zip "$GATEWAY_ZIP_URL" \
    && unzip clientportal.gw.zip -d . \
    && rm clientportal.gw.zip

FROM eclipse-temurin:8-jre

WORKDIR /app

COPY --from=gateway /app /app
COPY conf.yaml /app/root/conf.yaml
COPY scripts/docker-entrypoint.sh /usr/local/bin/ibkr-docker-entrypoint

RUN chmod +x /usr/local/bin/ibkr-docker-entrypoint

EXPOSE 5000

CMD ["ibkr-docker-entrypoint"]
