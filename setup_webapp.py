#!/usr/bin/python
#
# Please go through README file to set up the virtual env, aws security credentials and
# install the pre-reqs for this script to work.
#
# Assumptions:
# 1) You already have created a key pair to ssh into EC2 console
# for more info: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html
#
# 2) You have already created a web application server and installed and deployed
# your webapp (e.g. drupal or wordpress etc) in the server.
#
# 3) You have built an AMI out of your webapp in 2)


import logging
import argparse
import botocore.session
import config


def setup_vpc(client, cidr):
    """Creates a VPC."""
    res_vpc = client.create_vpc(
        CidrBlock=cidr,
        InstanceTenancy='default')
    logging.info('response for creating VPC = "%s"', res_vpc)
    return res_vpc['Vpc']['VpcId']


def create_subnet(client, cidr, vpc, az):
    """Creates a subnet and returns subnet id."""
    res_subnet = client.create_subnet(
        VpcId=vpc,
        CidrBlock=cidr,
        AvailabilityZone=az)
    logging.info('response for subnet = "%s"', res_subnet)
    return res_subnet['Subnet']['SubnetId']


def setup_bastion_host(client, ami, key, sg_id, subnet_id):
    """Creates an instance that can act like jump host."""
    response = client.run_instances(
        ImageId=ami,
        MinCount=1,
        MaxCount=1,
        KeyName=key,
        InstanceType='t2.micro',
        Monitoring={
            'Enabled': False
        },
        NetworkInterfaces=[
            {
                'DeviceIndex': 0,
                'SubnetId': subnet_id,
                'Groups': [
                    sg_id,
                ],
                'AssociatePublicIpAddress': True
            },
        ],
        EbsOptimized=False)
    logging.info('response for creating jump host = "%s"', response)


def create_security_group(client, sg_name, desc, vpc):
    """creates a security group."""
    response = client.create_security_group(
        GroupName=sg_name,
        Description=desc,
        VpcId=vpc)
    return response['GroupId']


def add_sg_rule(client, sg_id, protocol, cidr, from_port, to_port):
    """Adds ingress rule to the security group with source an IP."""
    response = client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpProtocol=protocol,
        FromPort=from_port,
        ToPort=to_port,
        CidrIp=cidr)
    logging.info('response for adding rule = "%s"', response)


def add_sg_rule_with_source_sg(client, sg_id, protocol, from_port, to_port, source_sg_id, vpc_id):
    """Adds ingress rule to the security group with source another security group."""
    response = client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                'IpProtocol': protocol,
                'FromPort': from_port,
                'ToPort': to_port,
                'UserIdGroupPairs': [
                    {
                        'GroupId': source_sg_id,
                        'VpcId': vpc_id,
                    },
                ],
            }
        ])
    logging.info('response for adding rule = "%s"', response)


def create_load_balancer(client, elb_name, pub_subnet_a,
                         pub_subnet_b, webserver_sg):
    """Creates a load balancer."""
    response = client.create_load_balancer(
        LoadBalancerName=elb_name,
        Listeners=[
            {
                'Protocol': 'HTTP',
                'LoadBalancerPort': 80,
                'InstanceProtocol': 'HTTP',
                'InstancePort': 80
            },
        ],
        Subnets=[
            pub_subnet_a,
            pub_subnet_b
        ],
        SecurityGroups=[
            webserver_sg,
        ])
    logging.info('response for creating ELB = "%s"', response)


def create_launch_config(client, name, ami, key, sg_id):
    """Creates a launch config."""
    response = client.create_launch_configuration(
        LaunchConfigurationName=name,
        ImageId=ami,
        KeyName=key,
        SecurityGroups=[
            sg_id,
        ],
        InstanceType='t2.micro',
        InstanceMonitoring={
            'Enabled': False
        },
        EbsOptimized=False)
    logging.info('response for creating launch config = "%s"', response)


def launch_rds(client, subnet_name, subnet_desc, priv_subnet_a,
               priv_subnet_b, vpc_db_sg, db_name, instance_id, db_username, db_pass):
    """Creates an RDS subnet group and launches an RDS instance."""
    response = client.create_db_subnet_group(
        DBSubnetGroupName=subnet_name,
        DBSubnetGroupDescription=subnet_desc,
        SubnetIds=[
            priv_subnet_a,
            priv_subnet_b
        ])
    logging.info('response for creating RDS subnet = "%s"', response)
    response1 = client.create_db_instance(
        DBName=db_name,
        DBInstanceIdentifier=instance_id,
        AllocatedStorage=5,
        DBInstanceClass='db.t2.micro',
        Engine='MySQL',
        MasterUsername=db_username,
        MasterUserPassword=db_pass,
        VpcSecurityGroupIds=[
            vpc_db_sg,
        ],
        DBSubnetGroupName=subnet_name,
        MultiAZ=False,
        LicenseModel='general-public-license')
    logging.info('response for creating RDS instance = "%s"', response1)


def create_asg(client, asg_name, lc_name, az_a, az_b, elb_name):
    """Creates an autoscaling group."""
    response = client.create_auto_scaling_group(
        AutoScalingGroupName=asg_name,
        LaunchConfigurationName=lc_name,
        MinSize=1,
        MaxSize=2,
        AvailabilityZones=[
            az_a,
            az_b
        ],
        LoadBalancerNames=[
            elb_name,
        ])
    logging.info('response for creating autoscaling group = "%s"', response)


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument("--aws-region", default="eu-west-1")
    parser.add_argument("--key-pair", default="bilal-dubizzle")
    args = parser.parse_args()
    session = botocore.session.get_session()
    # setup VPC and subnets
    ec2_client = session.create_client('ec2', args.aws_region)
    vpc_id = setup_vpc(ec2_client, config.vpc_cidr)
    pub_a_subnet_id = create_subnet(ec2_client, config.pub_subnet_a_cidr, vpc_id, config.az_a)
    pub_b_subnet_id = create_subnet(ec2_client, config.pub_subnet_b_cidr, vpc_id, config.az_b)
    priv_a_subnet_id = create_subnet(ec2_client, config.priv_subnet_a_cidr, vpc_id, config.az_a)
    priv_b_subnet_id = create_subnet(ec2_client, config.priv_subnet_b_cidr, vpc_id, config.az_b)
    # setup bastion host /jump server
    bastion_sg_id = create_security_group(ec2_client, config.bastion_sg,
                                          "security group for jump server", vpc_id)
    add_sg_rule(ec2_client, bastion_sg_id, "tcp", "0.0.0.0/0", 22, 22)
    setup_bastion_host(ec2_client, config.linux_free_ami, args.key_pair, bastion_sg_id, pub_a_subnet_id)
    # setup security group for webapp
    webserver_sg_id = create_security_group(ec2_client, config.webserver_sg,
                                            "security group for web server/app server", vpc_id)
    add_sg_rule(ec2_client, webserver_sg_id, "tcp", "0.0.0.0/0", 80, 80)
    add_sg_rule_with_source_sg(ec2_client, webserver_sg_id, "tcp", 22, 22, bastion_sg_id, vpc_id)
    # setup RDS
    dbserver_sg_id = create_security_group(ec2_client, config.dbserver_sg,
                                           "security group for database server to connect to app server",
                                           vpc_id)
    add_sg_rule_with_source_sg(ec2_client, dbserver_sg_id, "tcp", 3306, 3306, webserver_sg_id, vpc_id)
    rds_client = session.create_client('rds', args.aws_region)
    launch_rds(rds_client, config.rds_subnet, "bilal subnet group for RDS",
               priv_a_subnet_id, priv_b_subnet_id, dbserver_sg_id, config.db_name, config.db_instance_id,
               config.db_username, config.db_pass)
    # setup Load Balancer and Auto Scaling
    elb_client = session.create_client('elb', args.aws_region)
    create_load_balancer(elb_client, config.elb_name,
                         pub_a_subnet_id, pub_b_subnet_id, webserver_sg_id)
    as_client = session.create_client('autoscaling', args.aws_region)
    create_launch_config(as_client, config.lc_name, config.lc_ami, args.key_pair, webserver_sg_id)
    create_asg(as_client, config.asg_name, config.lc_name, config.az_a, config.az_b, config.elb_name)
