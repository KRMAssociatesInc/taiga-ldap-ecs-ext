# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2021-present Kaleidos Ventures SL

from .common import *
from ldap3 import Tls
import os, sys, ssl


#########################################
## GENERIC
#########################################
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT','5432'),
    }
}
SECRET_KEY = os.getenv('TAIGA_SECRET_KEY')

TAIGA_SITES_SCHEME = os.getenv('TAIGA_SITES_SCHEME')
TAIGA_SITES_DOMAIN = os.getenv('TAIGA_SITES_DOMAIN')
FORCE_SCRIPT_NAME = os.getenv('TAIGA_SUBPATH', '')

TAIGA_URL = f"{ TAIGA_SITES_SCHEME }://{ TAIGA_SITES_DOMAIN }{ FORCE_SCRIPT_NAME }"
SITES = {
        "api": { "name": "api", "scheme": TAIGA_SITES_SCHEME, "domain": TAIGA_SITES_DOMAIN },
        "front": { "name": "front", "scheme": TAIGA_SITES_SCHEME, "domain": f"{ TAIGA_SITES_DOMAIN }{ FORCE_SCRIPT_NAME }" }
}

INSTANCE_TYPE = "D"

WEBHOOKS_ENABLED = True

# Setting DEFAULT_PROJECT_SLUG_PREFIX to false
# removes the username from project slug
DEFAULT_PROJECT_SLUG_PREFIX = os.getenv('DEFAULT_PROJECT_SLUG_PREFIX', 'False') == 'True'

#########################################
## MEDIA
#########################################
MEDIA_URL = f"{ TAIGA_URL }/media/"
DEFAULT_FILE_STORAGE = "taiga_contrib_protected.storage.ProtectedFileSystemStorage"
THUMBNAIL_DEFAULT_STORAGE = DEFAULT_FILE_STORAGE

STATIC_URL = f"{ TAIGA_URL }/static/"


#########################################
## EMAIL
#########################################
# https://docs.djangoproject.com/en/3.1/topics/email/
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
CHANGE_NOTIFICATIONS_MIN_INTERVAL = 120  # seconds

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'system@taiga.io')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False') == 'True'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False') == 'True'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'user')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'password')


#########################################
## SESSION
#########################################
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True') == 'True'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True') == 'True'


#########################################
## EVENTS
#########################################
EVENTS_PUSH_BACKEND = "taiga.events.backends.rabbitmq.EventsPushBackend"

EVENTS_PUSH_BACKEND_URL = os.getenv('EVENTS_PUSH_BACKEND_URL')
if not EVENTS_PUSH_BACKEND_URL:
    EVENTS_PUSH_BACKEND_URL = f"amqp://{ os.getenv('RABBITMQ_USER') }:{ os.getenv('RABBITMQ_PASS') }@taiga-events-rabbitmq:5672/taiga"

EVENTS_PUSH_BACKEND_OPTIONS = {
    "url": EVENTS_PUSH_BACKEND_URL
}


#########################################
## TAIGA ASYNC
#########################################
CELERY_ENABLED = os.getenv('CELERY_ENABLED', 'True') == 'True'
from kombu import Queue  # noqa

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
if not CELERY_BROKER_URL:
    CELERY_BROKER_URL = f"amqp://{ os.getenv('RABBITMQ_USER') }:{ os.getenv('RABBITMQ_PASS') }@taiga-async-rabbitmq:5672/taiga"

CELERY_RESULT_BACKEND = None # for a general installation, we don't need to store the results
CELERY_ACCEPT_CONTENT = ['pickle', ]  # Values are 'pickle', 'json', 'msgpack' and 'yaml'
CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_TIMEZONE = 'Europe/Madrid'
CELERY_TASK_DEFAULT_QUEUE = 'tasks'
CELERY_QUEUES = (
    Queue('tasks', routing_key='task.#'),
    Queue('transient', routing_key='transient.#', delivery_mode=1)
)
CELERY_TASK_DEFAULT_EXCHANGE = 'tasks'
CELERY_TASK_DEFAULT_EXCHANGE_TYPE = 'topic'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'task.default'


#########################################
##  REGISTRATION
#########################################
PUBLIC_REGISTER_ENABLED = os.getenv('PUBLIC_REGISTER_ENABLED', 'False') == 'True'


#########################################
## CONTRIBS
#########################################

# SLACK
ENABLE_SLACK = os.getenv('ENABLE_SLACK', 'False') == 'True'
if ENABLE_SLACK:
    INSTALLED_APPS += [
        "taiga_contrib_slack"
    ]

# GITHUB AUTH
# WARNING: If PUBLIC_REGISTER_ENABLED == False, currently Taiga by default prevents the OAuth
# buttons to appear for both login and register
ENABLE_GITHUB_AUTH = os.getenv('ENABLE_GITHUB_AUTH', 'False') == 'True'
if PUBLIC_REGISTER_ENABLED and ENABLE_GITHUB_AUTH:
    INSTALLED_APPS += [
        "taiga_contrib_github_auth"
    ]
    GITHUB_API_CLIENT_ID = os.getenv('GITHUB_API_CLIENT_ID')
    GITHUB_API_CLIENT_SECRET = os.getenv('GITHUB_API_CLIENT_SECRET')

# GITLAB AUTH
# WARNING: If PUBLIC_REGISTER_ENABLED == False, currently Taiga by default prevents the OAuth
# buttons to appear for both login and register
ENABLE_GITLAB_AUTH = os.getenv('ENABLE_GITLAB_AUTH', 'False') == 'True'
if PUBLIC_REGISTER_ENABLED and ENABLE_GITLAB_AUTH:
    INSTALLED_APPS += [
        "taiga_contrib_gitlab_auth"
    ]
    GITLAB_API_CLIENT_ID = os.getenv('GITLAB_API_CLIENT_ID')
    GITLAB_API_CLIENT_SECRET = os.getenv('GITLAB_API_CLIENT_SECRET')
    GITLAB_URL = os.getenv('GITLAB_URL')

#########################################
## LDAP
#########################################

if os.getenv('TAIGA_ENABLE_LDAP', os.getenv('ENABLE_LDAP', 'False')).lower() == 'true':
    # see https://github.com/Monogramm/taiga-contrib-ldap-auth-ext
    print("Taiga contrib LDAP Auth Ext enabled", file=sys.stderr)
    INSTALLED_APPS += ["taiga_contrib_ldap_auth_ext"]

    if os.getenv('TAIGA_LDAP_USE_TLS', os.getenv('LDAP_START_TLS', 'False')).lower() == 'true':
        # Flag to enable LDAP with STARTTLS before bind
        LDAP_START_TLS = True
        LDAP_TLS_CERTS = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1, ciphers='RSA+3DES')
    else:
        LDAP_START_TLS = False

    LDAP_SERVER = os.getenv('TAIGA_LDAP_SERVER', os.getenv('LDAP_SERVER'))
    LDAP_PORT = int(os.getenv('TAIGA_LDAP_PORT', os.getenv('LDAP_PORT', '389')))

    # Full DN of the service account use to connect to LDAP server and search for login user's account entry
    # If LDAP_BIND_DN is not specified, or is blank, then an anonymous bind is attempated
    LDAP_BIND_DN = os.getenv('TAIGA_LDAP_BIND_DN', os.getenv('LDAP_BIND_DN'))
    LDAP_BIND_PASSWORD = os.getenv('TAIGA_LDAP_BIND_PASSWORD', os.getenv('LDAP_BIND_PASSWORD'))

    # Starting point within LDAP structure to search for login user
    # Something like 'ou=People,dc=company,dc=com'
    LDAP_SEARCH_BASE = os.getenv('TAIGA_LDAP_BASE_DN', os.getenv('LDAP_SEARCH_BASE'))

    # Additional search criteria to the filter (will be ANDed)
    #LDAP_SEARCH_FILTER_ADDITIONAL = '(mail=*)'

    # Names of attributes to get username, e-mail and full name values from
    # These fields need to have a value in LDAP
    LDAP_USERNAME_ATTRIBUTE = os.getenv('TAIGA_LDAP_USERNAME_ATTRIBUTE', os.getenv('LDAP_USERNAME_ATTRIBUTE'))
    LDAP_EMAIL_ATTRIBUTE = os.getenv('TAIGA_LDAP_EMAIL_ATTRIBUTE', os.getenv('LDAP_EMAIL_ATTRIBUTE'))
    LDAP_FULL_NAME_ATTRIBUTE = os.getenv('TAIGA_LDAP_FULL_NAME_ATTRIBUTE', os.getenv('LDAP_FULL_NAME_ATTRIBUTE'))

    # Option to not store the passwords in the local db
    if os.getenv('TAIGA_LDAP_SAVE_LOGIN_PASSWORD', os.getenv('LDAP_SAVE_LOGIN_PASSWORD', 'False')).lower() == 'false':
        LDAP_SAVE_LOGIN_PASSWORD = False

    # Fallback on normal authentication method if this LDAP auth fails. Uncomment to enable.
    LDAP_FALLBACK = os.getenv('TAIGA_LDAP_FALLBACK', os.getenv('LDAP_FALLBACK', 'normal'))

    # Function to map LDAP username to local DB user unique identifier.
    # Upon successful LDAP bind, will override returned username attribute
    # value. May result in unexpected failures if changed after the database
    # has been populated.
    def _ldap_slugify(uid: str) -> str:
        # example: force lower-case
        uid = uid.lower()
        return uid

    LDAP_MAP_USERNAME_TO_UID = _ldap_slugify

#########################################
## TELEMETRY
#########################################
ENABLE_TELEMETRY = os.getenv('ENABLE_TELEMETRY', 'True') == 'True'


#########################################
##  IMPORTERS
#########################################
ENABLE_GITHUB_IMPORTER = os.getenv('ENABLE_GITHUB_IMPORTER', 'False') == 'True'
if ENABLE_GITHUB_IMPORTER:
    IMPORTERS["github"] = {
        "active": True,
        "client_id": os.getenv('GITHUB_IMPORTER_CLIENT_ID'),
        "client_secret": os.getenv('GITHUB_IMPORTER_CLIENT_SECRET')
    }

ENABLE_JIRA_IMPORTER = os.getenv('ENABLE_JIRA_IMPORTER', 'False') == 'True'
if ENABLE_JIRA_IMPORTER:
    IMPORTERS["jira"] = {
        "active": True,
        "consumer_key": os.getenv('JIRA_IMPORTER_CONSUMER_KEY'),
        "cert": os.getenv('JIRA_IMPORTER_CERT'),
        "pub_cert": os.getenv('JIRA_IMPORTER_PUB_CERT')
    }

ENABLE_TRELLO_IMPORTER = os.getenv('ENABLE_TRELLO_IMPORTER', 'False') == 'True'
if ENABLE_TRELLO_IMPORTER:
    IMPORTERS["trello"] = {
        "active": True,
        "api_key": os.getenv('TRELLO_IMPORTER_API_KEY'),
        "secret_key": os.getenv('TRELLO_IMPORTER_SECRET_KEY')
    }