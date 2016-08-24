# simple-aws-webserver
A web server architecture on AWS using python boto SDK

Steps to run:

1. `pip install virtualenv`
2. `virtualenv venv`
3. `source venv/bin/activate`
4. `git clone https://github.com/bilalahmad99/simple-aws-webserver.git`
5. `cd simple-aws-webserver`
6. `python setup_webapp.py`

 `setup_webapp.py` has all the steps automated with following assumptions:

 1) You already have created a key pair to ssh into EC2 console
 for more info: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html

 2) You have already created a web application server and installed and deployed
 your webapp (e.g. drupal or wordpress etc) in the server.

 3) You have built an AMI out of your webapp in 2) 
