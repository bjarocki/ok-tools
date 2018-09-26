#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
import json
import os
import sys
import re
import requests
from jinja2 import Template
from time import time

# a Nomad Job Jinja2 template.
NOMAD_JOB_JINJA_TEMPLATE = """
{
  "Job": {
    "Datacenters": [
      "dc1"
    ],
    "ID": "{{SERVICE_ID}}",
    "Name": "{{SERVICE_NAME}}",
    "TaskGroups": [
      {
        "Count": {{CONTAINERS}},
        "Name": "{{SERVICE_NAME}}",
        "RestartPolicy": {
          "Attempts": 10,
          "Interval": 300000000000,
          "Delay": 10000000000,
          "Mode": "delay"
        },
        "Tasks": [
          {
            "Config": {
              "image": "{{DOCKER_IMAGE}}",
              "port_map": [
                {
                  "port": {{APPLICATION_PORT}}
                }
              ]
              {% if VOLUMES is defined %}
                ,"volumes" : [
                {% for v in VOLUMES %}"/srv/docker/storage/{{SERVICE_NAME}}/{{ v.name }}:{{ v.path }}"{% if not loop.last %},{% endif %}
                {% endfor %}
                ]
              {% endif %}
            },
            "Driver": "docker",
            {% if VARIABLES is defined %}
              "Env": {
                {% for key, value in VARIABLES.iteritems() %}"{{key}}": "{{value}}"{% if not loop.last %},{% endif %}
                {% endfor %}
               },
            {% endif %}
            "LogConfig": {
              "MaxFileSizeMB": 10,
              "MaxFiles": 10
            },
            "Name": "{{SERVICE_NAME}}",
            "Resources": {
              "CPU": {{CPU}},
              "DiskMB": {{DISK_SIZE}},
              "MemoryMB": {{RAM}},
              "Networks": [
                {
                  "DynamicPorts": [
                    {
                      "Label": "port",
                      "Value": 0
                    }
                  ],
                  "MBits": 1
                }
              ]
            },
            "Services": [
              {
                "Checks": [
                  {
                    "Interval": 10000000000,
                    "Name": "alive",
                    "Timeout": 5000000000,
                    "Type": "tcp"
                  }
                ],
                "Name": "{{SERVICE_NAME}}",
                "PortLabel": "port",
              {% if APPLICATION_TAGS is defined %}
                "Tags": [
                {% for tag in APPLICATION_TAGS %}"{{tag}}"{% if not loop.last %},{% endif %}
                {% endfor %}
               ]
              {% endif %}
              }
            ]
          }
        ]
      }
    ],
    "Type": "service",
    "Update": {
      "MaxParallel": 1,
      "Stagger": 10000000000
    }
  }
}
"""

JOB_DEFAULTS = {
  'CPU': 128,
  'RAM': 256,
  'DISK_SIZE': 500,
  'CONTAINERS': 1,
  'VARIABLES': {},
  'VOLUMES': {}
}

EXPECTED_ENVIRONMENT_VARIABLES = [
  'CI_PROJECT_NAME',
  'CI_COMMIT_SHA'
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


def docker_image():
    repo_name = os.environ.get('CI_PROJECT_NAME')
    commit_sha = os.environ.get('CI_COMMIT_SHA')

    if not repo_name:
        sys.exit('Missing CI_PROJECT_NAME')

    if not commit_sha or len(commit_sha) < 8:
        sys.exit('Missing (or short) CI_COMMIT_SHA')

    return '{0}/{1}:{2}'.format(DOCKER_REPOSITORY_HOST, repo_name, commit_sha[:8])


def environment_variables(defaults, secrets):
    try:
        for secret in secrets:
            defaults['VARIABLES'][secret] = os.environ.get(secret).strip()
        return True
    except:
        return False


def deployment_nomad_containers(configuration):
    try:
        return configuration.get('deployment').get('nomad').get('containers') or 1
    except:
        return 1


def application_port(configuration):
    try:
        return configuration.get('deployment').get('nomad').get('port') or sys.exit('Missing deployment.nomad.port in .repository-settings.yml')
    except:
        sys.exit('Missing deployment.nomad.port in .repository-settings.yml')


def application_tags(configuration):
    try:
        return configuration.get('deployment').get('nomad').get('tags') or sys.exit('Missing deployment.nomad.tags in .repository-settings.yml')
    except:
        sys.exit('Missing deployment.nomad.tags in .repository-settings.yml')


def application_volumes(configuration):
    try:
        return configuration.get('deployment').get('nomad').get('volumes') or []
    except:
        return []


def branch_name():
    return os.environ.get('CI_BUILD_REF_NAME') or sys.exit('Missing CI_BUILD_REF_NAME environment variable')


def core_variables(defaults, configuration):
    service_name = re.sub('[^0-9a-zA-Z-]+', '-', os.environ.get('CI_PROJECT_NAME'))
    service_id = re.sub('[^0-9a-zA-Z]+', '_', os.environ.get('CI_PROJECT_NAME'))

    defaults['SERVICE_NAME'] = '{0}-{1}'.format(re.sub('[^0-9a-zA-Z-]+', '-', branch_name()), service_name)
    defaults['SERVICE_ID'] = '{0}_{1}'.format(re.sub('[^0-9a-zA-Z]+', '_', branch_name()), service_id)

    defaults['APPLICATION_PORT'] = application_port(configuration)
    defaults['APPLICATION_TAGS'] = application_tags(configuration)
    defaults['DOCKER_IMAGE'] = docker_image()
    defaults['VOLUMES'] = application_volumes(configuration)
    defaults['CONTAINERS'] = deployment_nomad_containers(configuration)


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
    sanity_check(EXPECTED_ENVIRONMENT_VARIABLES + secrets) or sys.exit('sanity_check has failed')

    # populate configuration variables
    core_variables(JOB_DEFAULTS, configuration)

    # grab environment
    environment_variables(JOB_DEFAULTS, secrets)

    # prepare template
    template = Template(NOMAD_JOB_JINJA_TEMPLATE)

    # render final nomad json job
    nomad_job = template.render(JOB_DEFAULTS)

    # verify if json is valid
    try:
        parsed_job = json.loads(nomad_job)
    except Exception as e:
        print(nomad_job)
        raise

    r = requests.post(NOMAD_URL, json=parsed_job)

    if r.status_code != 200:
        sys.exit('Nomad job POST failed with http code {}'.format(r.status_code))
