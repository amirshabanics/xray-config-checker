FROM alpine:3.21.0
WORKDIR /app
# ARG XRAY_URL=https://github.com/GFW-knocker/Xray-core/releases/download/v1.8.23-mahsa-r3/Xray-linux-64.zip
# WORKDIR /app/configs
# RUN wget -O xray.zip $XRAY_URL \
#     && unzip xray.zip \
#     && rm xray.zip README.md LICENSE
# WORKDIR /app
# Or have a unstable network:
COPY xray/xray xray/geoip.dat xray/geosite.dat /app/
EXPOSE 10808
CMD ["/app/xray", "--config", "/app/configs/config.json"]