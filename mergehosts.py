#!/usr/bin/python
# merges a couple of files into a single hosts file
#
# Author: Thomas Delrue

import argparse
parser = argparse.ArgumentParser(description="MergeHosts merges a hosts file with local, hard-coded and untrusted hosts")
parser.add_argument("-v", "--verbose", help="Defines the verbosity level", action="count", default=0)
parser.add_argument("-l", "--local", help="Local hosts file containing one hostname per line (default value=local.hosts)", default="local.hosts", dest="local_hosts")
parser.add_argument("-u", "--untrusted", help="Untrusted hosts file containing one hostname per line (default value=untrusted.hosts)", default="untrusted.hosts", dest="untrusted_hosts")
parser.add_argument("-hc", "--hard", help="Hard coded hosts file formatted as <ip> <hostname> (default value=hardcoded.hosts)", default="hardcoded.hosts", dest="hard_coded")
parser.add_argument('--version', action='version', version='%(prog)s 0.1')
args = parser.parse_args()

print "args.verbose = [", args.verbose, "]"
print "args.local_hosts = [", args.local_hosts, "]"
print "args.untrusted_hosts = [", args.untrusted_hosts, "]"
print "args.hard_coded = [", args.hard_coded, "]"

