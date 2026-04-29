ARG GATEWAY_ZIP_URL=https://download2.interactivebrokers.com/portal/clientportal.gw.zip

FROM alpine:3.20 AS gateway

ARG GATEWAY_ZIP_URL

WORKDIR /app

RUN apk add --no-cache ca-certificates wget unzip \
    && wget -O clientportal.gw.zip "$GATEWAY_ZIP_URL" \
    && unzip clientportal.gw.zip -d . \
    && rm clientportal.gw.zip

FROM eclipse-temurin:8-jre

WORKDIR /app

COPY --from=gateway /app /app
COPY conf.yaml /app/root/conf.yaml

EXPOSE 5000

CMD ["sh", "bin/run.sh", "root/conf.yaml"]
