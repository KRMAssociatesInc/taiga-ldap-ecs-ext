FROM taigaio/taiga-back:latest

WORKDIR /taiga-back

COPY settings/config.py settings/config.py

RUN set -eux; \
  python -m pip install --no-cache-dir taiga-contrib-ldap-auth-ext;

EXPOSE 8000
ENTRYPOINT ["./docker/entrypoint.sh"]