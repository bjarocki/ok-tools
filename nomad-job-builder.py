#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
import json
import os
import sys
import requests
from base64 import decodestring
from jinja2 import Template
from time import time

# this is a Jinja2 template packed with base64
NOMAD_JOB_JINJA_TEMPLATE_BASE64 = "ewogICJKb2IiOiB7CiAgICAiQWxsQXRPbmNlIjogZmFsc2UsCiAgICAiQ29uc3RyYWludHMiOiBudWxsLAogICAgIkNyZWF0ZUluZGV4IjogNDE5MiwKICAgICJEYXRhY2VudGVycyI6IFsKICAgICAgImRjMSIKICAgIF0sCiAgICAiSUQiOiAie3tTRVJWSUNFX05BTUV9fSIsCiAgICAiTWV0YSI6IG51bGwsCiAgICAiTmFtZSI6ICJ7e1NFUlZJQ0VfTkFNRX19IiwKICAgICJQYXJhbWV0ZXJpemVkSm9iIjogbnVsbCwKICAgICJQYXJlbnRJRCI6ICIiLAogICAgIlBheWxvYWQiOiBudWxsLAogICAgIlBlcmlvZGljIjogbnVsbCwKICAgICJQcmlvcml0eSI6IDUwLAogICAgIlJlZ2lvbiI6ICJnbG9iYWwiLAogICAgIlN0YXR1cyI6ICJydW5uaW5nIiwKICAgICJTdGF0dXNEZXNjcmlwdGlvbiI6ICIiLAogICAgIlRhc2tHcm91cHMiOiBbCiAgICAgIHsKICAgICAgICAiQ29uc3RyYWludHMiOiBudWxsLAogICAgICAgICJDb3VudCI6IHt7Q09OVEFJTkVSU319LAogICAgICAgICJNZXRhIjogbnVsbCwKICAgICAgICAiTmFtZSI6ICJ7e1NFUlZJQ0VfTkFNRX19IiwKICAgICAgICAiUmVzdGFydFBvbGljeSI6IHsKICAgICAgICAgICJBdHRlbXB0cyI6IDEwLAogICAgICAgICAgIkRlbGF5IjogMjUwMDAwMDAwMDAsCiAgICAgICAgICAiSW50ZXJ2YWwiOiAzMDAwMDAwMDAwMDAsCiAgICAgICAgICAiTW9kZSI6ICJkZWxheSIKICAgICAgICB9LAogICAgICAgICJUYXNrcyI6IFsKICAgICAgICAgIHsKICAgICAgICAgICAgIkFydGlmYWN0cyI6IFtdLAogICAgICAgICAgICAiQ29uZmlnIjogewogICAgICAgICAgICAgICJpbWFnZSI6ICJ7e0RPQ0tFUl9JTUFHRX19IiwKICAgICAgICAgICAgICAicG9ydF9tYXAiOiBbCiAgICAgICAgICAgICAgICB7CiAgICAgICAgICAgICAgICAgICJwb3J0Ijoge3tBUFBMSUNBVElPTl9QT1JUfX0KICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICBdCiAgICAgICAgICAgICAgeyUgaWYgVk9MVU1FUyBpcyBkZWZpbmVkICV9CiAgICAgICAgICAgICAgICAsInZvbHVtZXMiIDogWwogICAgICAgICAgICAgICAgeyUgZm9yIHYgaW4gVk9MVU1FUyAlfSJ7eyB2IH19InslIGlmIG5vdCBsb29wLmxhc3QgJX0seyUgZW5kaWYgJX0KICAgICAgICAgICAgICAgIHslIGVuZGZvciAlfQogICAgICAgICAgICAgIHslIGVuZGlmICV9CiAgICAgICAgICAgIH0sCiAgICAgICAgICAgICJDb25zdHJhaW50cyI6IG51bGwsCiAgICAgICAgICAgICJEaXNwYXRjaFBheWxvYWQiOiBudWxsLAogICAgICAgICAgICAiRHJpdmVyIjogImRvY2tlciIsCiAgICAgICAgICAgIHslIGlmIFZBUklBQkxFUyBpcyBkZWZpbmVkICV9CiAgICAgICAgICAgICAgIkVudiI6IHsKICAgICAgICAgICAgICAgIHslIGZvciBrZXksIHZhbHVlIGluIFZBUklBQkxFUy5pdGVyaXRlbXMoKSAlfSJ7e2tleX19IjogInt7dmFsdWV9fSJ7JSBpZiBub3QgbG9vcC5sYXN0ICV9LHslIGVuZGlmICV9CiAgICAgICAgICAgICAgICB7JSBlbmRmb3IgJX0KICAgICAgICAgICAgICAgfSwKICAgICAgICAgICAgICB7JSBlbmRpZiAlfQogICAgICAgICAgICAiS2lsbFRpbWVvdXQiOiA1MDAwMDAwMDAwLAogICAgICAgICAgICAiTGVhZGVyIjogZmFsc2UsCiAgICAgICAgICAgICJMb2dDb25maWciOiB7CiAgICAgICAgICAgICAgIk1heEZpbGVTaXplTUIiOiAxMCwKICAgICAgICAgICAgICAiTWF4RmlsZXMiOiAxMAogICAgICAgICAgICB9LAogICAgICAgICAgICAiTWV0YSI6IG51bGwsCiAgICAgICAgICAgICJOYW1lIjogInt7U0VSVklDRV9OQU1FfX0iLAogICAgICAgICAgICAiUmVzb3VyY2VzIjogewogICAgICAgICAgICAgICJDUFUiOiB7e0NQVX19LAogICAgICAgICAgICAgICJEaXNrTUIiOiB7e0RJU0tfU0laRX19LAogICAgICAgICAgICAgICJJT1BTIjogMCwKICAgICAgICAgICAgICAiTWVtb3J5TUIiOiB7e1JBTX19LAogICAgICAgICAgICAgICJOZXR3b3JrcyI6IFsKICAgICAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICAgIkNJRFIiOiAiIiwKICAgICAgICAgICAgICAgICAgIkR5bmFtaWNQb3J0cyI6IFsKICAgICAgICAgICAgICAgICAgICB7CiAgICAgICAgICAgICAgICAgICAgICAiTGFiZWwiOiAicG9ydCIsCiAgICAgICAgICAgICAgICAgICAgICAiVmFsdWUiOiAwCiAgICAgICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgICBdLAogICAgICAgICAgICAgICAgICAiSVAiOiAiIiwKICAgICAgICAgICAgICAgICAgIk1CaXRzIjogMSwKICAgICAgICAgICAgICAgICAgIlB1YmxpYyI6IGZhbHNlLAogICAgICAgICAgICAgICAgICAiUmVzZXJ2ZWRQb3J0cyI6IG51bGwKICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICBdCiAgICAgICAgICAgIH0sCiAgICAgICAgICAgICJTZXJ2aWNlcyI6IFsKICAgICAgICAgICAgICB7CiAgICAgICAgICAgICAgICAiQ2hlY2tzIjogWwogICAgICAgICAgICAgICAgICB7CiAgICAgICAgICAgICAgICAgICAgIkFyZ3MiOiBudWxsLAogICAgICAgICAgICAgICAgICAgICJDb21tYW5kIjogIiIsCiAgICAgICAgICAgICAgICAgICAgIklkIjogIiIsCiAgICAgICAgICAgICAgICAgICAgIkluaXRpYWxTdGF0dXMiOiAiIiwKICAgICAgICAgICAgICAgICAgICAiSW50ZXJ2YWwiOiAxMDAwMDAwMDAwMCwKICAgICAgICAgICAgICAgICAgICAiTmFtZSI6ICJhbGl2ZSIsCiAgICAgICAgICAgICAgICAgICAgIlBhdGgiOiAiIiwKICAgICAgICAgICAgICAgICAgICAiUG9ydExhYmVsIjogIiIsCiAgICAgICAgICAgICAgICAgICAgIlByb3RvY29sIjogIiIsCiAgICAgICAgICAgICAgICAgICAgIlRpbWVvdXQiOiAyMDAwMDAwMDAwLAogICAgICAgICAgICAgICAgICAgICJUeXBlIjogInRjcCIKICAgICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgXSwKICAgICAgICAgICAgICAgICJJZCI6ICIiLAogICAgICAgICAgICAgICAgIk5hbWUiOiAie3tTRVJWSUNFX05BTUV9fSIsCiAgICAgICAgICAgICAgICAiUG9ydExhYmVsIjogInBvcnQiLAogICAgICAgICAgICAgIHslIGlmIEFQUExJQ0FUSU9OX1RBR1MgaXMgZGVmaW5lZCAlfQogICAgICAgICAgICAgICAgIlRhZ3MiOiBbCiAgICAgICAgICAgICAgICB7JSBmb3IgdGFnIGluIEFQUExJQ0FUSU9OX1RBR1MgJX0ie3t0YWd9fSJ7JSBpZiBub3QgbG9vcC5sYXN0ICV9LHslIGVuZGlmICV9CiAgICAgICAgICAgICAgICB7JSBlbmRmb3IgJX0KICAgICAgICAgICAgICAgXQogICAgICAgICAgICAgIHslIGVuZGlmICV9CiAgICAgICAgICAgICAgfQogICAgICAgICAgICBdLAogICAgICAgICAgICAiVGVtcGxhdGVzIjogW10sCiAgICAgICAgICAgICJVc2VyIjogIiIsCiAgICAgICAgICAgICJWYXVsdCI6IG51bGwKICAgICAgICAgIH0KICAgICAgICBdCiAgICAgIH0KICAgIF0sCiAgICAiVHlwZSI6ICJzZXJ2aWNlIiwKICAgICJVcGRhdGUiOiB7CiAgICAgICJNYXhQYXJhbGxlbCI6IDEsCiAgICAgICJTdGFnZ2VyIjogMTAwMDAwMDAwMDAKICAgIH0sCiAgICAiVmF1bHRUb2tlbiI6ICIiCiAgfQp9Cg=="

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
DOCKER_REPOSITORY_HOST = 'docker-registry.otwarte.xyz'
NOMAD_URL = os.environ.get('NOMAD_URL') or 'https://nomad.otwarte.xyz/v1/jobs'


def sanity_check(variables):
    try:
        for vname in variables:
            if not os.environ.get(vname):
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
    defaults['SERVICE_NAME'] = os.environ.get('DRONE_REPO_NAME')
    defaults['APPLICATION_PORT'] = application_port(configuration)
    defaults['APPLICATION_TAGS'] = application_tags(configuration)
    defaults['DOCKER_IMAGE'] = docker_image()


if __name__ == '__main__':
    # die if missing configuration file
    if not os.path.exists(CONFIGURATION_FILE):
        sys.exit(1)

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
