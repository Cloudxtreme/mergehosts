#!/usr/bin/python
# merges a couple of files into a single hosts file
#
# Author: Thomas Delrue

import argparse
import os
import random
import shutil
import sys
import time

VERBOSITY_ERR = 0
VERBOSITY_WARN = 1
VERBOSITY_INFO = 2
VERBOSITY_VERBOSE = 3

SINKHOLE = "0.0.0.0"
LOCALADDRESSES = { "127.0.0.1",  "::1" }

parser = argparse.ArgumentParser(description="MergeHosts merges a hosts file with local, hard-coded and untrusted hosts")
parser.add_argument("-v", "--verbose", help="Defines the verbosity level", action="count", default=0)
parser.add_argument("-l", "--local", metavar="<local>", help="Local hosts file containing one hostname per line (default value=local.hosts)", type=argparse.FileType('rt'), default="local.hosts", dest="local_hosts")
parser.add_argument("-u", "--untrusted", metavar="<untrusted>", help="Untrusted hosts file containing one hostname per line (default value=untrusted.hosts)", type=argparse.FileType('rt'), default="untrusted.hosts", dest="untrusted_hosts")
parser.add_argument("-hc", "--hard", metavar="<hard>", help="Hard coded hosts file formatted as <ip> <hostname> (default value=hardcoded.hosts)", type=argparse.FileType('rt'), default="hardcoded.hosts", dest="hard_coded")
parser.add_argument("-e",  "--external", metavar="<external>", help="File containing the external hosts formatted as <ip> <hostname>", type=argparse.FileType('rt'), default="hosts.txt", dest="external_hosts")
parser.add_argument("-d", "--destination", metavar="<dest>", help="Destination file (default value=/tmp/mergehosts.whatif)", default="/tmp/mergehosts.whatif", type=argparse.FileType('wt+'), dest="destination_file")
parser.add_argument('--version', action='version', version='%(prog)s 0.1')
args = parser.parse_args()

def VERBOSE(value):
    if args.verbose >= VERBOSITY_VERBOSE:
        print value

def INFO(value):
    if args.verbose >= VERBOSITY_INFO:
        print value

def WARN(value):
    if args.verbose >= VERBOSITY_WARN:
        print value

def print_argument_values():
    VERBOSE("args.verbose          = [" + str(args.verbose) + "]")
    VERBOSE("args.local_hosts      = [" + str(args.local_hosts) + "]")
    VERBOSE("args.untrusted_hosts  = [" + str(args.untrusted_hosts) + "]")
    VERBOSE("args.hard_coded       = [" + str(args.hard_coded) + "]")
    VERBOSE("args.external_hosts   = [" + str(args.external_hosts) + "]")
    VERBOSE("args.destination_file = [" + str(args.destination_file) + "]")

def get_temp_file():
    keepTrying = True

    # naive way of finding random temporary file name
    while keepTrying == True:
        tmp_file_path = "/tmp/mergehosts" + str(time.time()).replace('.', '') + ".hosts"
        keepTrying = os.path.isfile(tmp_file_path)

    VERBOSE("Temporary hosts file: " + tmp_file_path)

    return open(tmp_file_path, "w+")

def write_section_title(destination,  title):
    INFO("Adding " + title + "...")

    destination.write("#\n# ")
    destination.write(title)
    destination.write("\n")
    destination.write("#\n")


def write_entry(destination, hostname, ipvalue):
    destination.write(ipvalue)
    destination.write("\t")
    destination.write(hostname.lower())
    destination.write("\n")

def report_dupe_host(hostname, source):
    WARN("Duplicate host '" + hostname + "' (from " + source + ")")

def append_local_hosts(source, destination, hosts):
    write_section_title(destination, "Local Hosts")
    for line in source:
        line = line.strip()
        if line != "" and line[0] != "#":
            for local_address in LOCALADDRESSES:
                write_entry(destination, line, local_address)
                hosts[line] = 1     # when there are multiple LOCALADDRESSES, then yes this will be done multiple times for the same host

def append_untrusted_hosts(source, destination, hosts):
    write_section_title(destination, "Untrusted Hosts")
    for line in source:
        hostname = line.strip()
        if hostname != "" and hostname[0] != "#":
            if hosts.get(hostname) == None:
                write_entry(destination, hostname, SINKHOLE)
                hosts[hostname] = 1
            else:
                report_dupe_host(hostname, "untrusted")

def append_hardcoded_hosts(source, destination, hosts):
    write_section_title(destination, "Hard Coded Hosts")
    for line in source:
        line = line.strip()
        # TODO: extract hostname for dupe validation
        if line != "" and line[0] != '#':
            destination.write(line)
            destination.write('\n')

def append_external_hosts(source, destination, hosts):
    write_section_title(destination, "External Hosts")
    for line in source:
        line = line.strip()
        if line != "" and line[0] != '#':
            line = line.replace('\t',  ' ').split(' ',  1)[1].split(' ',  1)[0].strip()
            # note that some of these files explicitly define 'localhost'
            # in this script this is dealt with in the local.hosts file
            # so there is no need for us to re-add local hosts
            if line != "localhost":
                if hosts.get(line) == None:
                    write_entry(destination, line, SINKHOLE)
                    hosts[line] = 1
                else:
                    report_dupe_host(line, "external");

def main():
    print_argument_values()
    tmpFile = get_temp_file()

    # the file is built up in the order:
    # 1. local
    # 2. hard_coded
    # 3. untrusted
    # 4. external
    tmpFile.write("# Hosts file generated by MergeHosts (" + time.asctime() + ")\n")

    hosts = { }
    append_local_hosts(args.local_hosts, tmpFile, hosts)
    args.local_hosts.close()

    append_hardcoded_hosts(args.hard_coded, tmpFile, hosts)
    args.hard_coded.close()

    untrusted = append_untrusted_hosts(args.untrusted_hosts, tmpFile, hosts)
    args.untrusted_hosts.close()

    append_external_hosts(args.external_hosts, tmpFile, hosts)
    args.external_hosts.close()

    tmpFile.close()

    INFO(str(len(hosts)) + " host entries...")

    # commit the content
    shutil.copyfile(tmpFile.name, args.destination_file.name)
    os.remove(tmpFile.name)

if __name__ == '__main__':
    main()
