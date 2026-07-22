FROM nginx:1.27-alpine

RUN apk add --no-cache bash certbot openssl \
    && ln -sf /certs/crt.crt /etc/ssl/crt.crt \
    && ln -sf /certs/key.key /etc/ssl/key.key

COPY acme-entrypoint.sh /usr/local/bin/acme-entrypoint.sh

RUN sed -i 's/\r$//' /usr/local/bin/acme-entrypoint.sh \
    && chmod 0755 /usr/local/bin/acme-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/acme-entrypoint.sh"]
