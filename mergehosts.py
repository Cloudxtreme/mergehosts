#!/usr/bin/python
# merges a couple of files into a single hosts file
# Licensed under the GNU General Public License version 2

import argparse
import os
import random
import shutil
import socket
import sys
import time

VERBOSITY_ERR = 0
VERBOSITY_WARN = 1
VERBOSITY_INFO = 2
VERBOSITY_VERBOSE = 3

SINKHOLE = "0.0.0.0"
LOCALADDRESSES = set(["127.0.0.1", "::1"])
LOCALHOSTS = set(["localhost", socket.gethostname()])

parser = argparse.ArgumentParser(description="MergeHosts merges a hosts file with local, hard-coded and untrusted hosts")
parser.add_argument("-v", "--verbose", help="Defines the verbosity level", action="count", default=0)
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
    VERBOSE("args.hard_coded       = [" + str(args.hard_coded) + "]")
    VERBOSE("args.untrusted_hosts  = [" + str(args.untrusted_hosts) + "]")
    VERBOSE("args.external_hosts   = [" + str(args.external_hosts) + "]")
    VERBOSE("args.destination_file = [" + str(args.destination_file) + "]")

def get_temp_file():
    again = True

    # naive way of finding random temporary file name
    while again == True:
        tmp_file_path = "/tmp/mergehosts" + str(time.time()).replace('.', '') + ".hosts"
        again = os.path.isfile(tmp_file_path)

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
    WARN("Duplicate host '" + hostname + "' (duplicate in " + source + " hosts)")

def ignore_line(line):
    return line == "" or line[0] == '#'

def append_local_hosts(source, destination, hosts):
    write_section_title(destination, "Local Hosts")

    for line in source:
        hostname = line.strip()
        if ignore_line(hostname) == False:
            if not hostname in hosts:
                for local_address in LOCALADDRESSES:
                    write_entry(destination, hostname, local_address)
            hosts.add(line)

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
