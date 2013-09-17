'''
Network statistics collector

by freznicek
available under GPL v3

Pure python network analysis tool:
  * based on specified IP addresses
  * network analysis methods
    * ping


python nsc.py --verbose 
              --host=localhost --host=quad --host 192.168.2.1 \
              --host 192.168.2.2 --host=www.google.com --host=www.daniweb.com \
              --host=docs.python.org \
              --interval 3 --cfg-ping-cnt=3 --duration=60 \
              --save-data=/tmp/out.srl --load-data=/tmp/out.srl

'''

# imports
import re
import sys
import time
import pickle
import datetime
import optparse
import platform
import traceback
import subprocess


# methods
def ping(in_host, in_cnt = 3, in_to = 10, in_size = None):
  ''' ping using ping client
      return tuple (<loss-percentage>, <avg-time>, <exitcode>)
  '''
  
  # define ping command
  int_cmdline = ['ping', '-c'];
  if (platform.system() == 'Windows'):
    int_cmdline = ['ping', '-n'];
  int_cmdline.append(str(in_cnt));
  
  # append packet size (if defined)
  if (in_size != None):
    if (platform.system() == 'Windows'):
      int_cmdline.append('-l');
    else:
      int_cmdline.append('-s');
    int_cmdline.append(str(in_size));
  
  # append the host
  int_cmdline.append(str(in_host));
  
  int_re_loss = re.compile('([0-9]+)%');
  int_re_timing = re.compile('rtt min/avg/max/mdev = [0-9.]+/([0-9.]+)/([0-9.]+)/([0-9.]+)');
  if (platform.system() == 'Windows'):
    int_re_timing = re.compile('([0-9.]+)ms[ ]*$');
  
  p = subprocess.Popen(int_cmdline, stdout=subprocess.PIPE,
                       universal_newlines=True);
  stdout, stderr = p.communicate();
  int_ecode = p.returncode;
  int_loss = None;
  int_avg_time = None;
  
  for i_line in stdout.splitlines():
    if (int_re_loss.search(i_line)):
      int_loss = float(int_re_loss.search(i_line).groups()[0]);
    if (int_re_timing.search(i_line)):
      int_avg_time = float(int_re_timing.search(i_line).groups()[0]) / 1000.;
  
  return ((int_loss, int_avg_time, int_ecode));



def load_data(in_fn, in_opts):
  ''' load serialized data '''
  int_dict = None;
  try:
    fh = open(in_fn, 'r');
    int_dict = pickle.load(fh);
    fh.close();
  except Exception, e:
    if (in_opts['verbose']):
      traceback.print_exc();
    else:
      pass;
  
  if (int_dict != None):
    try:
      fh = open("%s.w" % in_fn, 'r');
      int_dict = pickle.load(fh);
      fh.close();
    except Exception, e:
      if (in_opts['verbose']):
        traceback.print_exc();
      else:
        pass;
  
  return(int_dict);

def save_data(in_fn, in_data, in_opts):
  ''' save serialized data '''
  try:
    fh = open("%s.w" % in_fn, 'w');
    pickle.dump(in_data, fh);
    fh.close();
    fh = open(in_fn, 'w');
    pickle.dump(in_data, fh);
    fh.close();
  except Exception, e:
    if (in_opts['verbose']):
      traceback.print_exc();
    else:
      pass;

def in_range(in_val, in_min, in_max):
  ''' is in_val in range interval <in_min, in_max> '''
  int_ret = ( (float(in_val) >= float(in_min)) and \
              (float(in_val) <= float(in_max)) );
  return(int_ret);

def compute_interval(in_cinterval, in_closs, in_opts):
  ''' compute current interval based on:
      * current interval 
      * cummulative loss 
      * adaptive iterval switches
  '''
  int_interval = in_cinterval;
  if( (in_opts['interval_max'] != None) and \
      (in_opts['interval_min'] != None) ):
    # adaptive interval enabled
    if (in_closs < 1.5):
      # all ok
      if (in_range(int_interval / 2.0,
                   in_opts['interval_min'], in_opts['interval_max'])):
        int_interval = int_interval / 2.0;
    else:
      # problem found
      if (in_range(int_interval * 2.0,
                   in_opts['interval_min'], in_opts['interval_max'])):
        int_interval = int_interval * 2.0;
  
  return(int_interval);



# main() definition
# ---------------------------------------------------------------------------
def main(in_opts):
  ''' main method (definition of main loop) '''
  # load serialized stream
  int_data = { };
  if (in_opts['load_data'] != None):
    int_data = load_data(in_opts['load_data'], in_opts);
  if (int_data == None):
    int_data = { };
  
  ts = time.time();
  i_interval = in_opts['interval'];
  while True:
    # loop the statistics
    i_ts = time.time();
    i_t_list = [ ];
    i_closs = 0.0;
    for i_ip in in_opts['hosts']:
      # browse the IPs
      loss, avg_time, ecode = ping(i_ip, in_cnt = in_opts['cfg_ping_cnt'],
                                   in_to = 10,
                                   in_size = in_opts['cfg_ping_size']);
      i_t_list.append( ( i_ip, loss, avg_time ) );
    
    # add the data to main dict
    int_data[i_ts] = i_t_list;
    
    if (in_opts['verbose']):
      i_dt = datetime.datetime.fromtimestamp(time.time());
      print "%04d-%02d-%02d %02d:%02d:%02d %s" % (i_dt.year, i_dt.month,
                                                  i_dt.day, i_dt.hour,
                                                  i_dt.minute, i_dt.second,
                                                  i_t_list);
    
    # save data
    if (in_opts['save_data'] != None):
      save_data(in_opts['save_data'], int_data, in_opts);
    
    if( (in_opts['duration'] > 0.0) and \
        ((in_opts['duration'] + ts) < time.time()) ):
      break;
    
    # sleep the given/computed interval
    i_interval = compute_interval(i_interval, i_closs, in_opts);
    time.sleep(i_interval);


# main() call
# ---------------------------------------------------------------------------
if __name__ == "__main__":

  # parameters definition and parsing
  # -------------------------------------------------------------------------
  usage_msg = "usage: %prog [options]";
  op = optparse.OptionParser(usage=usage_msg);

  # define parameters
  # -------------------------------------------------------------------------
  op.add_option("--load-data", dest="load_data", type="string",
                action="store", default=None,
                help="Load data from a file (def: %default)", metavar="IFN");
  op.add_option("--save-data", dest="save_data", type="string",
                action="store", default=None,
                help="Save/store data from a file (def: %default)",
                metavar="OFN");
  op.add_option("--hosts", dest="hosts", action="append", default=[ ],
                help="Add hosts for check (def: %default)");
  op.add_option("--cfg-ping-cnt", dest="cfg_ping_cnt", type="int",
                action="store", default=3,
                help="Ping count per batch (def: %default)", metavar="CPC");
  op.add_option("--cfg-ping-size", dest="cfg_ping_size", type="int",
                action="store", default=None,
                help="Ping count per batch (def: %default)", metavar="CPC");
  op.add_option("--interval", dest="interval", type="float",
                action="store", default=10.0,
                help="Report interval in sec[s] (def: %default)",
                metavar="I");
  op.add_option("--interval-max", dest="interval_max", type="float",
                action="store", default=None,
                help="Adaptive interval - maximum in sec[s] (def: %default)");
  op.add_option("--interval-min", dest="interval_min", type="float",
                action="store", default=None,
                help="Adaptive interval - minimum in sec[s] (def: %default)");
  op.add_option("--duration", dest="duration", type="float",
                action="store", default=0.0,
                help="Measurement duration in sec[s] (def: %default)",
                metavar="DUR");
  op.add_option("--help-long", dest="help_long",
                action="store_true", default=False,
                help="Long help");
  op.add_option("-v", "--verbose", dest="verbose",
                action="store_true", default=False,
                help="Verbose mode");
  op.add_option("--site-a-defaults", dest="site_a_defaults",
                action="store_true", default=False,
                help="Apply site A defaults");
  op.add_option("--report-data", dest="report_data",
                action="store_true", default=False,
                help="Report stored data [use with load-data] (def: %default)");
  (opts, args) = op.parse_args();
  
  if (opts.help_long):
    print __doc__;
    op.print_help();
    sys.exit(0);
  
  int_opts = { };
  int_opts = eval('%s' % opts);
  
  # defaults
  if (int_opts['site_a_defaults']):
    int_opts['hosts'] = [ '10.0.0.138', '192.168.10.1',   '192.168.10.2',
                          '192.168.10.100', '192.168.10.101', '192.168.10.103',
                          '192.168.10.104', '192.168.10.105', '192.168.10.106',
                          '192.168.10.107', '192.168.10.108' ];
    int_opts['interval'] = 60 * 60;
    dt = datetime.datetime.fromtimestamp(time.time());
    int_opts['save_data'] = 'nsc_%s%s.srl' % (dt.year, dt.month);
    int_opts['load_data'] = int_opts['save_data'];
    int_opts['cfg_ping_cnt'] = 5;
    int_opts['cfg_ping_size'] = 1000;
  
  if (int_opts['report_data']):
    # report current data
    int_data = load_data(int_opts['load_data'], int_opts);
    if (int_data != None):
      for i_ts in sorted(int_data.keys()):
        # browse timestamps
        i_dt = datetime.datetime.fromtimestamp(i_ts);
        print "%04d-%02d-%02d %02d:%02d:%02d %s" % (i_dt.year, i_dt.month,
                                                    i_dt.day, i_dt.hour,
                                                    i_dt.minute, i_dt.second,
                                                    int_data[i_ts]);
    else:
      print 'No data found';
    sys.exit(0);
  else:
    # no report
    if (len(int_opts['hosts']) == 0):
      print >> sys.stderr, "No host given, cannot continue...";
      print __doc__;
      op.print_help();
      sys.exit(1);
  
  # call main() method
  main(int_opts);


# ---------------------------------------------------------------------------
# eof
# ---------------------------------------------------------------------------
