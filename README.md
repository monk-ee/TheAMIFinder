TheAMIFinder
============
A utility for finding valid amis with minimal effort. It can output to json if necessary.

Syntax
========

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

Configuration
==========
Requires IAM Roles or a boto config file (~/.boto):

    [Credentials]
    aws_access_key_id = <your access key>
    aws_secret_access_key = <your secret key>



Proxy
==========
You may need to add proxy information to your .boto file

    [Boto]
    debug = 0
    num_retries = 10

    proxy = myproxy.com
    proxy_port = 8080


Dependencies
==========
 + PyYAML==3.10
 + boto==2.27.0
 + argparse==1.2.1


Author
==========
Contact me on twitter @monkee_magic
