mergehosts
==========
There exist websites that maintain custom version of hosts file which block out unwanted hosts. Examples are hpHosts (http://www.hosts-file.net) and WinHelp2002 (http://winhelp2002.mvps.org/hosts.htm).
I got tired of having to edit the file every time to add my own set of blocked hosts after downloading newer versions of these files.
I wrote this script that lets you maintain your own set of untrusted, hard coded and local host names and merge this together with the downloaded hosts file.

By default, the script dumps its output to /tmp/mergehosts.whatif so that you may inspect the file before committing it to your /etc/hosts file. (but if so desired, you can instruct the script to immedately overwrite your /etc/hosts file as well)

	$ ./mergehosts.py -h
	usage: mergehosts.py [-h] [-v] [-u <untrusted>] [-hc <hard>] [-e <external>]
        	             [-d <dest>] [--version]
	
	MergeHosts merges a hosts file with local, hard-coded and untrusted hosts
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --verbose         Defines the verbosity level
	  -u <untrusted>, --untrusted <untrusted>
	                        Untrusted hosts file containing one hostname per line
	                        (default value=untrusted.hosts)
	  -hc <hard>, --hard <hard>
	                        Hard coded hosts file formatted as <ip> <hostname>
	                        (default value=hardcoded.hosts)
	  -e <external>, --external <external>
	                        File containing the external hosts formatted as <ip>
	                        <hostname>
	  -d <dest>, --destination <dest>
	                        Destination file (default
                        	value=/tmp/mergehosts.whatif)
	  --version             show program's version number and exit
