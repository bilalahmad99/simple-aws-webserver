# the variable names

az_a = "eu-west-1a"
az_b = "eu-west-1b"
pub_subnet_a_cidr = "10.0.1.0/24"
pub_subnet_b_cidr = "10.0.2.0/24"
priv_subnet_a_cidr = "10.0.3.0/24"
priv_subnet_b_cidr = "10.0.4.0/24"

asg_name = "bilal-asg"
lc_name = "bilal-lc"
elb_name = "bilal-lb"
vpc_cidr = "10.0.0.0/16"
linux_free_ami = "ami-f9dd458a"
# place the ami id for the deployed webapp ami
lc_ami = ""
# RDS vars
db_name = "bilal_database"
db_instance_id = "bilal-db-instance"
db_username = "db_bilal"
db_pass = "db_bilal"
rds_subnet = "bilal-db-subnet-group"
# security groups
bastion_sg = "bilal-bastion-sg"
webserver_sg = "bilal-webserver-sg"
dbserver_sg = "bilal-dbserver-sg"
