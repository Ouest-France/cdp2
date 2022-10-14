#!/usr/bin/python
# -*-coding:Utf-8 -*
#
# connects to a SOLIDserver, create dns server, zone and records
#
##########################################################

import logging
import pprint
import os, sys
import uuid

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from SOLIDserverRest import *
from SOLIDserverRest import adv as sdsadv

logging.basicConfig(format='[%(filename)s:%(lineno)d] %(levelname)s: %(message)s',
                    level=logging.INFO)

# configuration - to be adapted
SDS_HOST = "ipam.ouest-france.fr"
SDS_LOGIN = "037207T"
SDS_PWD = "10RDPACpdr35"

logging.info("create a connection to the SOLIDserver")

sds = sdsadv.SDS(ip_address=SDS_HOST,
                 user=SDS_LOGIN,
                 pwd=SDS_PWD)

try:
    sds.connect(method="native")
except SDSError as e:
    logging.error(e)
    exit()

logging.info(sds)

# --------------------------
logging.info("create DNS record")
name = "testmmr"
dns_rr = sdsadv.DNS_record(sds, name)
dns_rr.set_zone(zone)
dns_rr.set_type('A', ip='127.1.2.3')
dns_rr.create()

logging.info(dns_rr)
dns_rr.delete()

dns_rr = sdsadv.DNS_record(sds, name)
dns_rr.set_zone(dns_zone)
dns_rr.set_type('CNAME', target='ingress.dev-k8s.of.ouest-france.fr')
dns_rr.create()

logging.info(dns_rr)
dns_rr.delete()

dns_rr = sdsadv.DNS_record(sds, name)
dns_rr.set_zone(dns_zone)
dns_rr.set_type('MX', priority=10, target="foo.bar")
dns_rr.create()

logging.info(dns_rr)
dns_rr.delete()

# --------------------------
logging.info("cleaning")
dns_zone.delete()
dns.delete()

del sds
