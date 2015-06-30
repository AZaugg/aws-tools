#!/usr/bin/python
#
# Get a list of ELBs that are exposed to the world
# with no SGs restricting access
#

import boto.ec2.elb
import boto.ec2

REGION = "ap-southeast-2"

# AWS connections
rc = boto.ec2.elb.connect_to_region(REGION)
ec2_rc = boto.ec2.connect_to_region(REGION)

elbs = rc.get_all_load_balancers()

for elb in elbs:

    # Only check ELB internet-facing ELB schemes
    if elb.scheme != "internet-facing":
        continue

    sgs_all = ec2_rc.get_all_security_groups(group_ids=[str(x) for x in elb.security_groups])

    for sg in sgs_all:
        if not sg.rules:
            continue

        for rule in sg.rules:
           for zx in rule.grants:
               if str(zx.cidr_ip) != "0.0.0.0/0":
                   continue

               elb_name = elb.name
               print elb_name
