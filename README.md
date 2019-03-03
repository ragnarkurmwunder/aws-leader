# Determine a leader in AWS Autoscaling group

This script determines which instance is a leader in an autoscaling group.

It does not communicate between instances to establish an agreement nor uses locking.

Leader is established by having alphabetically first instance ID in sorted instance ID list.

## Usage

```
./aws-leader.py
```

* Exit code 0 - current instance is a leader
* Exit code 1 - current instance is not a leader

## Install

1. Download the script and place it to `/usr/local/bin/aws-leader.py`
1. Give it execution rights `chmod 755 /usr/local/bin/aws-leader.py`

When running into trouble with missing Python libs:

```
$ sudo pip install botocore boto3 awscli --upgrade
```

Note that upgrading system `awscli` is needed,
because it is dependent `botocore` which will be upgraded
and `awscli` conflicts with new `botocore`
which is needed for `boto3`.
