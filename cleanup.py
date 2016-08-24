#!/usr/bin/python
#
# NOTE: This script only cleans up the part that is most involved in aws billing
# It will not remove the VPC and subnets and security groups that you created
# with setup_webapp.py. So if you want to run setup_webapp.py again, make sure
# to remove the previous VPC stuff or comment out that section from the script.
#

import config
import logging
import argparse
import botocore.session


def delete_autoscaling_group(client, asg_name, lc_name):
    client.delete_auto_scaling_group(
        AutoScalingGroupName=asg_name,
        ForceDelete=True)
    logging.info('autoscaling group "%s" deleted', asg_name)
    client.delete_launch_configuration(
        LaunchConfigurationName=lc_name)
    logging.info('launch config "%s" deleted', lc_name)


def delete_loadbalancer(client, elb_name):
    response = client.delete_load_balancer(
        LoadBalancerName=elb_name)
    logging.info('response for deleting ELB = "%s"', response)


def delete_instances(client):
    response = client.deregister_image(
        ImageId='string'
    )
    logging.info('response for deresgistering image = "%s"', response)
    response_snap = client.delete_snapshot(
        SnapshotId='string'
    )
    logging.info('response for deleting snapshot = "%s"', response_snap)
    response_instance = client.terminate_instances(
        InstanceIds=[
            'string',
        ]
    )
    logging.info('response for deleting instance = "%s"', response_instance)


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument("--aws-region", default="eu-west-1")
    args = parser.parse_args()
    session = botocore.session.get_session()

    asg_client = session.create_client('autoscaling', args.aws_region)
    delete_autoscaling_group(asg_client, config.asg_name, config.lc_name)
    elb_client = session.create_client('elb', args.aws_region)
    delete_loadbalancer(elb_client, config.elb_name)
