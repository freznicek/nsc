nsc
===

Network statistics collaborator

Idea
----

Let's have home or SOHO network.
There will be day when you start feeling that yo need to monitor the network.

In my particular case I had SOHO network between two offices (two buildings), main office had ISP provider connection to internet (main network segment) and the other remote office with wifi bridge (remote network segment).
Mutual signal optical visibility is moderate at 75 meters, much betetr at 100 meters.

Having multiple network segments connected via 802.11n wireless bridges is sensitive to signal distortion specially in the case when you use indoor wifi omnidirirectional antennas instead of proper outdoor directional point-to-point ones.


Network statistics collaborator (nsc) helps to detect and collect needed socket timing information among existing LAN segments.
The principle is very easy:
 * selected machines (among LAN segments) run nsc and collect network statistics
 * nsc collects information and store it in text platform independent format
 * nsc can run on every platform (hard requirement is Win/Linux)
 * nsc uses adaptive timing to sample / collect information more frequently on network failure
 * nsc is capable of displaying netwok statistic data
 * nsc network analysis methods
   * ping packet loss
   * ping packet timing
   * TODO

Example of usage
----------------
  * running nsc in incremental interval non-adaptive mode forever
  <pre><code>$ python nsc.py [--verbose]
                              --host=localhost --host ...
                              --interval 3600 --cfg-ping-cnt=5
                              --save-data=nsc.srl --load-data=nsc.srl
  </code></pre>
  
  * running nsc in incremental interval non-adaptive mode for 1 hour
  <pre><code>$ python nsc.py [--verbose]
                              --host=localhost --host ...
                              --interval $((30*60)) --interval-min $((60))  --interval-max $((60*60))
                              --cfg-ping-cnt=5 --duration=60
                              --save-data=nsc.srl --load-data=nsc.srl
  </code></pre>
  
  * displaying current results
  <pre><code>$ python nsc.py --load-data=nsc.srl --report-data
  </code></pre>

Command-line interface
----------------------

<pre><code>$
 python nsc.py --help-long

Network statistics collaborator

Pure python network analysis tool:
  * based on specified IP addresses
  * network analysis methods
    * ping


python nsc.py --verbose
              --host=localhost --host=quad --host ...
              --interval 3 --cfg-ping-cnt=3 --duration=60
              --save-data=/tmp/out.srl --load-data=/tmp/out.srl


Usage: nsc.py [options]

Options:
  -h, --help            show this help message and exit
  --load-data=IFN       Load data from a file (def: none)
  --save-data=OFN       Save/store data from a file (def: none)
  --hosts=HOSTS         Add hosts for check (def: [])
  --cfg-ping-cnt=CPC    Ping count per batch (def: 3)
  --interval=I          Report interval in sec[s] (def: 10.0)
  --interval-max=INTERVAL_MAX
                        Adaptive interval - maximum in sec[s] (def: none)
  --interval-min=INTERVAL_MIN
                        Adaptive interval - minimum in sec[s] (def: none)
  --duration=DUR        Measurement duration in sec[s] (def: 0.0)
  --help-long           Long help
  -v, --verbose         Verbose mode
  --site-a-defaults     Apply site A defaults
  --report-data         Report stored data [use with load-data] (def: False)
</code></pre>


TO-DO list:
----------

 * another network analysis to be added
 * pylint fixes
 * test suite

Requirements
------------

python 2.4+

Files
-----

nsc.py                main python engine

License
-------

GPL v2
http://www.gnu.org/licenses/gpl-2.0.html


.eof
