#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""TheAMIFinder.py: A utility for stretching ec2 volumes with minimal effort."""

# Requires: your boto config file (~/.boto) to contain your aws credentials
#
# image_ids (list) – A list of strings with the image IDs wanted
# owners (list) – A list of owner IDs, the special strings ‘self’, ‘amazon’, and ‘aws-marketplace’, may be used to describe images owned by you, Amazon or AWS Marketplace respectively
# executable_by (list) – Returns AMIs for which the specified user ID has explicit launch permissions
# filters (dict) – Optional filters that can be used to limit the results returned. Filters are provided in the form of a dictionary consisting of filter names as the key and filter values as the value. The set of allowable filter names/values is dependent on the request being performed. Check the EC2 API guide for details.
# dry_run (bool) – Set to True if the operation should not actually run.

__project__ = 'TheAMIFinder'
__author__ = "monkee"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "monk-ee"
__email__ = "magic.monkee.magic@gmail.com"
__status__ = "Development"

import boto.ec2, boto.sns
import yaml, sys,logging,time,os,re
import argparse, operator


class TheAMIFinder(object):
    """
    usage: TheAMIFinder.py [-h] [-d] [-j] [--region REGION] [--owner OWNER]
                           [--dev DEV] [--virt VIRT] [--arch ARCH] [--desc DESC]

    A utility for finding valid amis with minimal effort. It can output to
    json if necessary.

    optional arguments:
      -h, --help       show this help message and exit
      -d, --dryrun     Fake runs for testing purposes.
      -j, --json       Output as json.
      --region REGION  Region to search in. Defaults to all.
      --owner OWNER    An Amazon Marketplace Image Owner.
      --dev DEV        The root device type; either ebs or instance-store.
      --virt VIRT      The virtualization type; either paravirtual or hvm.
      --arch ARCH      The virtual processor architecture; either i386 or x86_64.
      --desc DESC      The description of the image you are looking for; supports
                       wildcards.

    Example Names
    #u'amzn-ami-hvm-2013.09.2.x86_64-s3'
    #u'amzn-ami-hvm-2012.09.1.x86_64-ebs'
    #u'amzn-ami-pv-2014.03.1.x86_64-ebs' u'Amazon Linux AMI x86_64 PV EBS'
    #u'amzn-ami-minimal-pv-2014.03.0.x86_64-s3' u'Amazon Linux AMI x86_64 MINIMAL S3'
    #u'amzn-ami-pv-2012.09.1.x86_64-s3' u'Amazon Linux AMI x86_64 S3'
    #u'amzn-ami-minimal-pv-2013.09.0.i386-ebs' u'Amazon Linux AMI i386 MINIMAL EBS'
    #u'amzn-ami-pv-2013.03.1.i386-ebs' u'Amazon Linux AMI i386 PV EBS'
    """
    conn = ""
    config = ""
    timestamp = time.strftime("%d/%m/%Y %H:%M:%S")
    owners = []
    virtualization_type = 'paravirtual'
    architecture = 'i386'
    root_device_type = 'instance-store'
    description = 'Amazon Linux AMI x86_64 PV EBS'
    region = 'all'
    regions = []
    image_ids = ""

    def __init__(self, arg):
        try:
            self.owners.append(arg.owner)
            self.dryrun = arg.dryrun
            self.virtualization_type = arg.virt
            self.architecture = arg.arch
            self.root_device_type = arg.dev
            self.region = arg.region
        except BaseException as emsg:
            sys.exit("Missing arguments" + str(emsg))
        self.check_arguments()
        self.load_configuration()
        self.ec2_connect_to_region()
        if self.region == 'all':
            self.get_all_regions()
            self.search_all_regions_for_instance()
        else:
            self.ec2_reconnect_to_region(self.region)
            self.search_for_instance()


    def load_configuration(self):
        try:
            config_str = open(os.path.dirname(os.path.abspath(__file__)) + '/config.yml', 'r')
            self.config = yaml.load(config_str)
            logfile = os.path.dirname(os.path.abspath(__file__)) + "/" + self.config['general']['logfile']
            logging.basicConfig(filename=logfile, level=logging.INFO)
        except IOError as error:
            exit("Could not load config.yml: " + str(error))
        except:
            raise
            exit("Unexpected error:" + str(sys.exc_info()[0]))

    def check_arguments(self):
        pass

    def ec2_connect_to_region(self):
        try:
            self.conn = boto.ec2.connect_to_region(self.config['general']['default_region'])
        except:
            #done again
            exit("Failed to connect to EC2")

    def get_all_regions(self):
        try:
            self.regions = self.conn.get_all_regions()
        except:
            exit("Failed to get regions")

    def ec2_reconnect_to_region(self, region):
        try:
            self.conn = boto.ec2.connect_to_region(region)
        except:
            #done again
            exit("Failed to connect to EC2")

    def search_all_regions_for_instance(self):
        for region in self.regions:
            self.ec2_reconnect_to_region(region.name)
            images = self.conn.get_all_images(owners=self.owners,filters={'virtualization_type' : self.virtualization_type, 'architecture' : self.architecture,'root_device_type' : self.root_device_type, 'description' : self.description})
            #now parse name to look for the newest date
            if(images.__len__() == 0):
                exit("No images could be found matching your search criteria.")
            version = {}
            for ami in images:
                short_string = ami.name[12:-10]
                new_string = short_string.replace(".","")
                version[ami.id] = new_string
            print(region.name)
            print(version)
            print(max(version.iteritems(), key=operator.itemgetter(1))[0])

    def search_for_instance(self):
        images = self.conn.get_all_images(owners=self.owners,filters={'virtualization_type' : self.virtualization_type, 'architecture' : self.architecture,'root_device_type' : self.root_device_type, 'description' : self.description})
        #now parse name to look for the newest date
        if(images.__len__() == 0):
            exit("No images could be found matching your search criteria.")
        version = {}
        for ami in images:
            short_string = ami.name[12:-10]
            new_string = short_string.replace(".","")
            version[ami.id] = new_string
        print(max(version.iteritems(), key=operator.itemgetter(1))[0])




if __name__ == "__main__":
    #grab the arguments when the script is ran
    parser = argparse.ArgumentParser(description='A utility for finding valid amis with minimal effort. It can output to json if necessary.')
    parser.add_argument('-d', '--dryrun', action='store_true', default=False, help='Fake runs for testing purposes.')
    parser.add_argument('-j', '--json', action='store_true', default=False, help='Output as json.')
    parser.add_argument('--region',  default='all', help='Region to search in. Defaults to all.')
    parser.add_argument('--owner',  default='amazon', help='A list of owner IDs, the special strings ‘self’, ‘amazon’, and ‘aws-marketplace’, may be used to describe images owned by you, Amazon or AWS Marketplace respectively.')
    parser.add_argument('--dev',  default='ebs', help='The root device type; either ebs or instance-store.')
    parser.add_argument('--virt',  default='paravirtual', help='The virtualization type; either paravirtual or hvm.')
    parser.add_argument('--arch',  default='x86_64', help='The virtual processor architecture; either i386 or x86_64.')
    parser.add_argument('--desc',  default='Amazon Linux AMI', help='The description of the image you are looking for; supports wildcards.')
    args = parser.parse_args()
    ts = TheAMIFinder(args)


