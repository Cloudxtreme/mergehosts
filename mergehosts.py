#!/usr/bin/python
# merges a couple of files into a single hosts file
# Licensed under the GNU General Public License version 2

import argparse
import os
import random
import shutil
import socket
import sys
import tempfile
import time

VERBOSITY_ERR = 0
VERBOSITY_WARN = 1
VERBOSITY_INFO = 2
VERBOSITY_VERBOSE = 3

SINKHOLE = "0.0.0.0"
LOCALADDRESSES = set(["127.0.0.1", "::1"])
LOCALHOSTS = set(["localhost", socket.gethostname()])

default_destination = "/tmp/mergehosts.whatif"
if os.name == "nt":
    default_destination = "%TMP%\\mergehosts.whatif"

parser = argparse.ArgumentParser(description="MergeHosts merges a hosts file with local, hard-coded and untrusted hosts")
parser.add_argument("-v", "--verbose", help="Defines the verbosity level", action="count", default=0)
parser.add_argument("-u", "--untrusted", metavar="<untrusted>", help="Untrusted hosts file containing one hostname per line (default value=untrusted.hosts)", type=argparse.FileType('rt'), default="untrusted.hosts", dest="untrusted_hosts")
parser.add_argument("-hc", "--hard", metavar="<hard>", help="Hard coded hosts file formatted as <ip> <hostname> (default value=hardcoded.hosts)", type=argparse.FileType('rt'), default="hardcoded.hosts", dest="hard_coded")
parser.add_argument("-e",  "--external", metavar="<external>", help="File containing the external hosts formatted as <ip> <hostname>", type=argparse.FileType('rt'), default="hosts.txt", dest="external_hosts")
parser.add_argument("-d", "--destination", metavar="<dest>", help="Destination file (default value=" + default_destination + ")", default=default_destination, type=argparse.FileType('wt+'), dest="destination_file")
parser.add_argument('--version', action='version', version='%(prog)s 0.1')
args = parser.parse_args()

'''
Outputs verbose information
    @value: value to display
'''
def VERBOSE(value):
    if args.verbose >= VERBOSITY_VERBOSE:
        print value

'''
Outputs informational information
    @value: value to display
'''
def INFO(value):
    if args.verbose >= VERBOSITY_INFO:
        print value

'''
Outputs warning information
    @value: value to display
'''
def WARN(value):
    if args.verbose >= VERBOSITY_WARN:
        sys.stderr.write("WARNING: " + str(value) + "\n")

'''
Outputs error information
    @value: value to display
'''
def ERR(value):
    sys.stderr.write("ERROR: " + str(value) + "\n")

'''
Prints all configurable values
'''
def print_argument_values():
    VERBOSE("args.verbose          = [" + str(args.verbose) + "]")
    VERBOSE("args.hard_coded       = [" + str(args.hard_coded) + "]")
    VERBOSE("args.untrusted_hosts  = [" + str(args.untrusted_hosts) + "]")
    VERBOSE("args.external_hosts   = [" + str(args.external_hosts) + "]")
    VERBOSE("args.destination_file = [" + str(args.destination_file) + "]")

'''
Gets a temporary file
'''
def get_temp_file():
    result = tempfile.mkstemp()[1]
    VERBOSE("Temporary hosts file: " + result)
    return open(result, "w+")

'''
Writes the section header
    @destination: stream to write to
    @title: section title
'''
def write_section_title(destination,  title):
    INFO("Adding " + title + "...")

    destination.write("#\n# ")
    destination.write(title)
    destination.write("\n")
    destination.write("#\n")

'''
Writes a hosts file entry
    @destination: stream to write to
    @hostname: name of the host to bind to an ip
    @ipvalue: value to bind the host to
'''
def write_entry(destination, hostname, ipvalue):
    destination.write(ipvalue)
    destination.write("\t")
    destination.write(hostname.lower())
    destination.write("\n")

'''
Reports a duplicate host
    @hostname: name of the duplicate host
    @source: first duplicate mentioning location
'''
def report_dupe_host(hostname, source):
    WARN("Duplicate host '" + hostname + "' (duplicate in " + source + " hosts)")

'''
Returns whether or not the line should/can be ignored
    @line: line to validate
'''
def ignore_line(line):
    return line == "" or line[0] == '#'

'''
Ensures the local hosts are in the hosts file with local addresses
    @source: local host entries
    @destination: stream to write to
    @hosts: set of hosts that keeps track of which hosts have already been seen
'''
def append_local_hosts(source, destination, hosts):
    write_section_title(destination, "Local Hosts")

    for line in source:
        hostname = line.strip()
        if ignore_line(hostname) == False:
            if not hostname in hosts:
                for local_address in LOCALADDRESSES:
                    write_entry(destination, hostname, local_address)
            hosts.add(line)

'''
Ensures all untrusted hosts are sinkholed
    @source: untrusted host entries
    @destination: stream to write to
    @hosts: set of hosts that keeps track of which hosts have already been seen
'''
def append_untrusted_hosts(source, destination, hosts):
    write_section_title(destination, "Untrusted Hosts")

    for line in source:
        hostname = line.strip()
        if ignore_line(hostname) == False:
            if not hostname in hosts:
                write_entry(destination, hostname, SINKHOLE)
                hosts.add(hostname)
            else:
                report_dupe_host(hostname, "untrusted")

'''
Creates all entries that are tied to either the sinkhole or a real address
    @name: section name
    @source: external or hard coded host entries
    @destination: stream to write to
    @hosts: set of hosts that keeps track of which hosts have already been seen
    @use_sinkhole: whether the target address is the sinkhole or the one specified by the entry
'''
def process_tuple_file(name, source, destination, hosts, use_sinkhole):
    write_section_title(destination, name + " Hosts")
    for entry in source:
        line = entry
        # strip comments if any
        pound_index = line.find('#')
        if pound_index >= 0:
            line = line[:pound_index]
        
        line = line.replace('\t', ' ').strip()
        if line != "":
            # split in IP and host name
            split = line.split(' ', 1)
            if len(split) == 2:
                split[1] = split[1].strip()

                # since we do localhosts first, they will never be coded to another machine or to the sinkhole
                if not split[1] in hosts:
                    hosts.add(split[1])
                    if use_sinkhole == False:
                        write_entry(destination, split[1], split[0])
                    else:
                        write_entry(destination, split[1], SINKHOLE)
                else:
                    report_dupe_host(split[1], name)
            else:
                exit("The " + name + " hosts file contains an incorrectly formed line \"" + entry[:len(entry) - 2] + "\"")

'''
Entry point
'''
def main():
    print_argument_values()
    tmp_file = get_temp_file()

    # the file is built up in the order:
    # 1. local
    # 2. hard_coded
    # 3. untrusted
    # 4. external
    tmp_file.write("# Hosts file generated by MergeHosts (" + time.asctime() + ")\n")

    hosts = set([])
    append_local_hosts(LOCALHOSTS, tmp_file, hosts)

    process_tuple_file("Hard Coded", args.hard_coded, tmp_file, hosts, False)
    args.hard_coded.close()

    untrusted = append_untrusted_hosts(args.untrusted_hosts, tmp_file, hosts)
    args.untrusted_hosts.close()

    process_tuple_file("External", args.external_hosts, tmp_file, hosts, True)
    args.external_hosts.close()

    INFO(str(len(hosts)) + " host entries...")
    tmp_file.write("# This file contains " + str(len(hosts)) + " host entries...\n")
    tmp_file.close()

    # commit the content
    shutil.copyfile(tmp_file.name, args.destination_file.name)
    os.remove(tmp_file.name)

if __name__ == '__main__':
    main()
