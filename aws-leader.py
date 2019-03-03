#!/usr/bin/python

from botocore.exceptions import ClientError, BotoCoreError
from requests import RequestException
import boto3
import logging
import requests
import sys

# https://hackernoon.com/do-as-i-say-not-as-i-do-get-your-ec2-instance-name-without-breaking-your-infrastructure-1da4a0963af0
def get_current_name_id_region():
  try:
    r = requests.get("http://169.254.169.254/latest/dynamic/instance-identity/document")
    r.raise_for_status()
  except RequestException as e:
    logging.exception(e)
    return None

  try:
    response_json = r.json()
  except ValueError as e:
    logging.exception(e)
    return None

  region = response_json.get('region')
  instance_id = response_json.get('instanceId')

  if not (region and instance_id):
    logging.error('Invalid region: {} or instance_id: {}'.format(region, instance_id))
    return None

  try:
    ec2 = boto3.resource('ec2', region_name=region)
    instance = ec2.Instance(instance_id)
    tags = instance.tags
  except (ValueError, ClientError, BotoCoreError) as e:
    logging.exception(e)
    return None

  tags = tags or []
  names = [tag.get('Value') for tag in tags if tag.get('Key') == 'Name']
  name = names[0] if names else None
  if name is None:
    return None

  return {'name': name, 'id': instance_id, 'region': region}

def get_leader_id(name, region):

  filters = [
    {
      'Name' : 'instance-state-name',
      'Values' : ['running']
    },
    {
      'Name': 'tag:Name',
      'Values': [name]
    }
  ]

  try:
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_instances(Filters=filters)
  except (ValueError, ClientError, BotoCoreError) as e:
    logging.exception(e)
    return None

  members = []

  for reservation in response["Reservations"]:
      for instance in reservation["Instances"]:
          members.append(instance['InstanceId'])

  members = sorted(members)
  leader_id = members[0]
  return leader_id

def main():
  current = get_current_name_id_region()
  if current is None:
    sys.exit(1)
  current_id = current['id']

  leader_id = get_leader_id(current['name'], current['region'])
  if leader_id is None:
    sys.exit(1)

  if current_id == leader_id:
    sys.exit(0)
  else:
    sys.exit(1)

main()
