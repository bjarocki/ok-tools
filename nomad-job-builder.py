#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
import json
import os
import sys
import re
import requests
from base64 import decodestring
from jinja2 import Template
from time import time

# this is a Jinja2 template packed with base64
NOMAD_JOB_JINJA_TEMPLATE_BASE64 = "ewogICJKb2IiOiB7CiAgICAiQWxsQXRPbmNlIjogZmFsc2UsCiAgICAiQ29uc3RyYWludHMiOiBudWxsLAogICAgIkNyZWF0ZUluZGV4IjogNDE5MiwKICAgICJEYXRhY2VudGVycyI6IFsKICAgICAgImRjMSIKICAgIF0sCiAgICAiSUQiOiAie3tTRVJWSUNFX0lEfX0iLAogICAgIk1ldGEiOiBudWxsLAogICAgIk5hbWUiOiAie3tTRVJWSUNFX05BTUV9fSIsCiAgICAiUGFyYW1ldGVyaXplZEpvYiI6IG51bGwsCiAgICAiUGFyZW50SUQiOiAiIiwKICAgICJQYXlsb2FkIjogbnVsbCwKICAgICJQZXJpb2RpYyI6IG51bGwsCiAgICAiUHJpb3JpdHkiOiA1MCwKICAgICJSZWdpb24iOiAiZ2xvYmFsIiwKICAgICJTdGF0dXMiOiAicnVubmluZyIsCiAgICAiU3RhdHVzRGVzY3JpcHRpb24iOiAiIiwKICAgICJUYXNrR3JvdXBzIjogWwogICAgICB7CiAgICAgICAgIkNvbnN0cmFpbnRzIjogbnVsbCwKICAgICAgICAiQ291bnQiOiB7e0NPTlRBSU5FUlN9fSwKICAgICAgICAiTWV0YSI6IG51bGwsCiAgICAgICAgIk5hbWUiOiAie3tTRVJWSUNFX05BTUV9fSIsCiAgICAgICAgIlJlc3RhcnRQb2xpY3kiOiB7CiAgICAgICAgICAiQXR0ZW1wdHMiOiAxMCwKICAgICAgICAgICJEZWxheSI6IDI1MDAwMDAwMDAwLAogICAgICAgICAgIkludGVydmFsIjogMzAwMDAwMDAwMDAwLAogICAgICAgICAgIk1vZGUiOiAiZGVsYXkiCiAgICAgICAgfSwKICAgICAgICAiVGFza3MiOiBbCiAgICAgICAgICB7CiAgICAgICAgICAgICJBcnRpZmFjdHMiOiBbXSwKICAgICAgICAgICAgIkNvbmZpZyI6IHsKICAgICAgICAgICAgICAiaW1hZ2UiOiAie3tET0NLRVJfSU1BR0V9fSIsCiAgICAgICAgICAgICAgInBvcnRfbWFwIjogWwogICAgICAgICAgICAgICAgewogICAgICAgICAgICAgICAgICAicG9ydCI6IHt7QVBQTElDQVRJT05fUE9SVH19CiAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgXQogICAgICAgICAgICAgIHslIGlmIFZPTFVNRVMgaXMgZGVmaW5lZCAlfQogICAgICAgICAgICAgICAgLCJ2b2x1bWVzIiA6IFsKICAgICAgICAgICAgICAgIHslIGZvciB2IGluIFZPTFVNRVMgJX0ie3sgdiB9fSJ7JSBpZiBub3QgbG9vcC5sYXN0ICV9LHslIGVuZGlmICV9CiAgICAgICAgICAgICAgICB7JSBlbmRmb3IgJX0KICAgICAgICAgICAgICB7JSBlbmRpZiAlfQogICAgICAgICAgICB9LAogICAgICAgICAgICAiQ29uc3RyYWludHMiOiBudWxsLAogICAgICAgICAgICAiRGlzcGF0Y2hQYXlsb2FkIjogbnVsbCwKICAgICAgICAgICAgIkRyaXZlciI6ICJkb2NrZXIiLAogICAgICAgICAgICB7JSBpZiBWQVJJQUJMRVMgaXMgZGVmaW5lZCAlfQogICAgICAgICAgICAgICJFbnYiOiB7CiAgICAgICAgICAgICAgICB7JSBmb3Iga2V5LCB2YWx1ZSBpbiBWQVJJQUJMRVMuaXRlcml0ZW1zKCkgJX0ie3trZXl9fSI6ICJ7e3ZhbHVlfX0ieyUgaWYgbm90IGxvb3AubGFzdCAlfSx7JSBlbmRpZiAlfQogICAgICAgICAgICAgICAgeyUgZW5kZm9yICV9CiAgICAgICAgICAgICAgIH0sCiAgICAgICAgICAgICAgeyUgZW5kaWYgJX0KICAgICAgICAgICAgIktpbGxUaW1lb3V0IjogNTAwMDAwMDAwMCwKICAgICAgICAgICAgIkxlYWRlciI6IGZhbHNlLAogICAgICAgICAgICAiTG9nQ29uZmlnIjogewogICAgICAgICAgICAgICJNYXhGaWxlU2l6ZU1CIjogMTAsCiAgICAgICAgICAgICAgIk1heEZpbGVzIjogMTAKICAgICAgICAgICAgfSwKICAgICAgICAgICAgIk1ldGEiOiBudWxsLAogICAgICAgICAgICAiTmFtZSI6ICJ7e1NFUlZJQ0VfTkFNRX19IiwKICAgICAgICAgICAgIlJlc291cmNlcyI6IHsKICAgICAgICAgICAgICAiQ1BVIjoge3tDUFV9fSwKICAgICAgICAgICAgICAiRGlza01CIjoge3tESVNLX1NJWkV9fSwKICAgICAgICAgICAgICAiSU9QUyI6IDAsCiAgICAgICAgICAgICAgIk1lbW9yeU1CIjoge3tSQU19fSwKICAgICAgICAgICAgICAiTmV0d29ya3MiOiBbCiAgICAgICAgICAgICAgICB7CiAgICAgICAgICAgICAgICAgICJDSURSIjogIiIsCiAgICAgICAgICAgICAgICAgICJEeW5hbWljUG9ydHMiOiBbCiAgICAgICAgICAgICAgICAgICAgewogICAgICAgICAgICAgICAgICAgICAgIkxhYmVsIjogInBvcnQiLAogICAgICAgICAgICAgICAgICAgICAgIlZhbHVlIjogMAogICAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgICAgXSwKICAgICAgICAgICAgICAgICAgIklQIjogIiIsCiAgICAgICAgICAgICAgICAgICJNQml0cyI6IDEsCiAgICAgICAgICAgICAgICAgICJQdWJsaWMiOiBmYWxzZSwKICAgICAgICAgICAgICAgICAgIlJlc2VydmVkUG9ydHMiOiBudWxsCiAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgXQogICAgICAgICAgICB9LAogICAgICAgICAgICAiU2VydmljZXMiOiBbCiAgICAgICAgICAgICAgewogICAgICAgICAgICAgICAgIkNoZWNrcyI6IFsKICAgICAgICAgICAgICAgICAgewogICAgICAgICAgICAgICAgICAgICJBcmdzIjogbnVsbCwKICAgICAgICAgICAgICAgICAgICAiQ29tbWFuZCI6ICIiLAogICAgICAgICAgICAgICAgICAgICJJZCI6ICIiLAogICAgICAgICAgICAgICAgICAgICJJbml0aWFsU3RhdHVzIjogIiIsCiAgICAgICAgICAgICAgICAgICAgIkludGVydmFsIjogMTAwMDAwMDAwMDAsCiAgICAgICAgICAgICAgICAgICAgIk5hbWUiOiAiYWxpdmUiLAogICAgICAgICAgICAgICAgICAgICJQYXRoIjogIiIsCiAgICAgICAgICAgICAgICAgICAgIlBvcnRMYWJlbCI6ICIiLAogICAgICAgICAgICAgICAgICAgICJQcm90b2NvbCI6ICIiLAogICAgICAgICAgICAgICAgICAgICJUaW1lb3V0IjogMjAwMDAwMDAwMCwKICAgICAgICAgICAgICAgICAgICAiVHlwZSI6ICJ0Y3AiCiAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgIF0sCiAgICAgICAgICAgICAgICAiSWQiOiAiIiwKICAgICAgICAgICAgICAgICJOYW1lIjogInt7U0VSVklDRV9OQU1FfX0iLAogICAgICAgICAgICAgICAgIlBvcnRMYWJlbCI6ICJwb3J0IiwKICAgICAgICAgICAgICB7JSBpZiBBUFBMSUNBVElPTl9UQUdTIGlzIGRlZmluZWQgJX0KICAgICAgICAgICAgICAgICJUYWdzIjogWwogICAgICAgICAgICAgICAgeyUgZm9yIHRhZyBpbiBBUFBMSUNBVElPTl9UQUdTICV9Int7dGFnfX0ieyUgaWYgbm90IGxvb3AubGFzdCAlfSx7JSBlbmRpZiAlfQogICAgICAgICAgICAgICAgeyUgZW5kZm9yICV9CiAgICAgICAgICAgICAgIF0KICAgICAgICAgICAgICB7JSBlbmRpZiAlfQogICAgICAgICAgICAgIH0KICAgICAgICAgICAgXSwKICAgICAgICAgICAgIlRlbXBsYXRlcyI6IFtdLAogICAgICAgICAgICAiVXNlciI6ICIiLAogICAgICAgICAgICAiVmF1bHQiOiBudWxsCiAgICAgICAgICB9CiAgICAgICAgXQogICAgICB9CiAgICBdLAogICAgIlR5cGUiOiAic2VydmljZSIsCiAgICAiVXBkYXRlIjogewogICAgICAiTWF4UGFyYWxsZWwiOiAxLAogICAgICAiU3RhZ2dlciI6IDEwMDAwMDAwMDAwCiAgICB9LAogICAgIlZhdWx0VG9rZW4iOiAiIgogIH0KfQo="

JOB_DEFAULTS = {
  'CPU': 1024,
  'RAM': 512,
  'DISK_SIZE': 500,
  'CONTAINERS': 1,
  'VARIABLES': {}
}

EXPECTED_ENVIRONMENT_VARIABLES = [
  'DRONE_REPO_NAME',
  'DRONE_COMMIT'
]

CONFIGURATION_FILE = '.repository-settings.yml'
DOCKER_REPOSITORY_HOST = os.environ.get('DOCKER_REPOSITORY_HOST') or 'docker-registry.otwarte.xyz'
NOMAD_URL = os.environ.get('NOMAD_URL') or 'https://nomad.otwarte.xyz/v1/jobs'


def sanity_check(variables):
    try:
        for vname in variables:
            if not os.environ.get(vname):
                print('missing secret : {0}'.format(vname))
                return False

        return True
    except:
        return False


def notify():
    slack_url = os.environ.get('SLACK_URL')
    slack_channel = os.environ.get('SLACK_CHANNEL') or '#tech-ops'

    if not slack_url:
        return False

    message = {
      'channel': slack_channel,
      'attachments': [
        {
          'color': '#4cc0b5',
          'footer_icon': 'https://internal-ops.otwarte.xyz/ok-logo.png',
          'footer': 'otwarte_klatki',
          'text': "{0}\n\n<{1}|szczegóły zmiany tutaj>".format(os.environ.get('DRONE_COMMIT_MESSAGE'), os.environ.get('DRONE_COMMIT_LINK')),
          'thumb_url': 'https://internal-ops.otwarte.xyz/rocket.png',
          'title': 'Aktualizacja {0} trafila na serwer'.format(os.environ.get('DRONE_REPO_NAME')),
          'title_link': 'https://{0}.otwarte.xyz'.format(os.environ.get('DRONE_REPO_NAME')),
          'ts': int(time())
        }
      ]
    }

    author_avatar = os.environ.get('DRONE_COMMIT_AUTHOR_AVATAR')

    # let's add personal touch here
    if author_avatar:
        message['attachments'][0]['author_name'] = os.environ.get('DRONE_COMMIT_AUTHOR')
        message['attachments'][0]['author_link'] = 'https://github.com/{}'.format(os.environ.get('DRONE_COMMIT_AUTHOR'))
        message['attachments'][0]['author_icon'] = author_avatar

    r = requests.post(slack_url, json=message)

    return r.status_code == 200


def docker_image():
    repo_name = os.environ.get('DRONE_REPO_NAME')
    commit_sha = os.environ.get('DRONE_COMMIT')

    if not repo_name or not commit_sha or len(commit_sha) < 7:
        sys.exit(1)

    return '{0}/{1}:{2}'.format(DOCKER_REPOSITORY_HOST, repo_name, commit_sha[:7])


def environment_variables(defaults, secrets):
    try:
        for secret in secrets:
            defaults['VARIABLES'][secret] = os.environ.get(secret)
        return True
    except:
        return False


def application_port(configuration):
    try:
        return configuration.get('deployment').get('nomad').get('port') or sys.exit(1)
    except:
        sys.exit(1)


def application_tags(configuration):
    try:
        return configuration.get('deployment').get('nomad').get('tags') or sys.exit(1)
    except:
        sys.exit(1)


def core_variables(defaults, configuration):
    service_name = re.sub('[^0-9a-zA-Z-]+', '-', os.environ.get('DRONE_REPO_NAME'))
    service_id = re.sub('[^0-9a-zA-Z]+', '_', os.environ.get('DRONE_REPO_NAME'))

    defaults['SERVICE_NAME'] = '{0}-{1}'.format(re.sub('[^0-9a-zA-Z-]+', '-', os.environ.get('DRONE_REPO_BRANCH')), service_name)
    defaults['SERVICE_ID'] = '{0}_{1}'.format(re.sub('[^0-9a-zA-Z]+', '_', os.environ.get('DRONE_REPO_BRANCH')), service_id)

    defaults['APPLICATION_PORT'] = application_port(configuration)
    defaults['APPLICATION_TAGS'] = application_tags(configuration)
    defaults['DOCKER_IMAGE'] = docker_image()


if __name__ == '__main__':
    # die if missing configuration file
    if not os.path.exists(CONFIGURATION_FILE):
        sys.exit('Missing configuration file [{0}]'.format(CONFIGURATION_FILE))

    # get configuration
    with open(CONFIGURATION_FILE) as fp:
        configuration = yaml.load(fp.read())

    # get a list of secrets
    try:
        secrets = configuration.get('deployment').get('nomad').get('secrets') or []
    except:
        secrets = []

    # make a sanity check
    sanity_check(EXPECTED_ENVIRONMENT_VARIABLES + secrets) or sys.exit(1)

    # unpack jinja template
    job_template = decodestring(NOMAD_JOB_JINJA_TEMPLATE_BASE64)

    # populate configuration variables
    core_variables(JOB_DEFAULTS, configuration)

    # grab environment
    environment_variables(JOB_DEFAULTS, secrets)

    # prepare template
    template = Template(job_template)

    # render final nomad json job
    nomad_job = template.render(JOB_DEFAULTS)

    # verify if json is valid
    try:
        nomad_job = json.loads(nomad_job)
    except:
        sys.exit(1)

    r = requests.post(NOMAD_URL, json=nomad_job)

    if r.status_code != 200:
        sys.exit(1)

    notify()
