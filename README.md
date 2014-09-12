mergehosts
==========
There exist websites that maintain custom version of hosts file which block out unwanted hosts. Examples are hpHosts (http://www.hosts-file.net) and WinHelp2002 (http://winhelp2002.mvps.org/hosts.htm).
I got tired of having to edit the file every time to add my own set of blocked hosts after downloading newer versions of these files.
I wrote this script that lets you maintain your own set of untrusted, hard coded and local host names and merge this together with the downloaded hosts file.

By default, the script dumps its output to /tmp/mergehosts.whatif so that you may inspect the file before committing it to your /etc/hosts file. (but if so desired, you can instruct the script to immedately overwrite your /etc/hosts file as well)

<code>
$ ./mergehosts.py -h
usage: mergehosts.py [-h] [-v] [-u %lt;untrusted%gt;] [-hc %lt;hard%gt;] [-e %lt;external%gt;]
                     [-d %lt;dest%gt;] [--version]

MergeHosts merges a hosts file with local, hard-coded and untrusted hosts

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Defines the verbosity level
  -u %lt;untrusted%gt;, --untrusted %lt;untrusted%gt;
                        Untrusted hosts file containing one hostname per line
                        (default value=untrusted.hosts)
  -hc %lt;hard%gt;, --hard %lt;hard%gt;
                        Hard coded hosts file formatted as %lt;ip%gt; %lt;hostname%gt;
                        (default value=hardcoded.hosts)
  -e %lt;external%gt;, --external %lt;external%gt;
                        File containing the external hosts formatted as %lt;ip%gt;
                        %lt;hostname%gt;
  -d %lt;dest%gt;, --destination %lt;dest%gt;
                        Destination file (default
                        value=/tmp/mergehosts.whatif)
  --version             show program's version number and exit
</code>
