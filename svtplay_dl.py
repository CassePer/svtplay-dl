#!/usr/bin/env python
import sys
import re
import os
from optparse import OptionParser
import logging

from svtplay.log import log
from svtplay.utils import get_http_data, select_quality

from svtplay.service.aftonbladet import Aftonbladet
from svtplay.service.dr import Dr
from svtplay.service.expressen import Expressen
from svtplay.service.hbo import Hbo
from svtplay.service.justin import Justin
from svtplay.service.kanal5 import Kanal5
from svtplay.service.kanal9 import Kanal9
from svtplay.service.nrk import Nrk
from svtplay.service.qbrick import Qbrick
from svtplay.service.ruv import Ruv
from svtplay.service.sr import Sr
from svtplay.service.svtplay import Svtplay
from svtplay.service.tv4play import Tv4play
from svtplay.service.urplay import Urplay
from svtplay.service.viaplay import Viaplay

__version__ = "0.8.2013.01.15"

class Options:
    """
    Options used when invoking the script from another Python script.
    
    Simple container class used when calling get_media() from another Python
    script. The variables corresponds to the command line parameters parsed
    in main() when the script is called directly.
    
    When called from a script there are a few more things to consider:
    
    * Logging is done to 'log'. main() calls setup_log() which sets the
      logging to either stdout or stderr depending on the silent level.
      A user calling get_media() directly can either also use setup_log()
      or configure the log manually.

    * Progress information is printed to 'progress_stream' which defaults to
      sys.stderr but can be changed to any stream.
    
    * Many errors results in calls to system.exit() so catch 'SystemExit'-
      Exceptions to prevent the entire application from exiting if that happens.
    
    """

    def __init__(self):
        self.output = None
        self.resume = False
        self.live = False
        self.silent = False
        self.quality = None
        self.hls = False
        self.other = None

def get_media(url, options):
    sites = [Aftonbladet(), Dr(), Expressen(), Hbo(), Justin(), Kanal5(), Kanal9(),
             Nrk(), Qbrick(), Ruv(), Sr(), Svtplay(), Tv4play(), Urplay(), Viaplay()]
    stream = None
    for i in sites:
        if i.handle(url):
            stream = i
            break
    if not stream:
        log.error("That site is not supported. Make a ticket or send a message")
        sys.exit(2)

    if not options.output or os.path.isdir(options.output):
        data = get_http_data(url)
        match = re.search("(?i)<title.*>\s*(.*?)\s*</title>", data)
        if match:
            if sys.version_info > (3, 0):
                title = re.sub('[^\w\s-]', '', match.group(1)).strip().lower()
                if options.output:
                    options.output = options.output + re.sub('[-\s]+', '-', title)
                else:
                    options.output = re.sub('[-\s]+', '-', title)
            else:
                title = unicode(re.sub('[^\w\s-]', '', match.group(1)).strip().lower())
                if options.output:
                    options.output = unicode(options.output + re.sub('[-\s]+', '-', title))
                else:
                    options.output = unicode(re.sub('[-\s]+', '-', title))

    stream.get(options, url)

def setup_log(silent):
    if silent:
        stream = sys.stderr
        level = logging.WARNING
    else:
        stream = sys.stdout
        level = logging.INFO

    fmt = logging.Formatter('%(levelname)s %(message)s')
    hdlr = logging.StreamHandler(stream)
    hdlr.setFormatter(fmt)

    log.addHandler(hdlr)
    log.setLevel(level)

def main():
    """ Main program """
    usage = "usage: %prog [options] url"
    parser = OptionParser(usage=usage, version=__version__)
    parser.add_option("-o", "--output",
        metavar="OUTPUT", help="Outputs to the given filename.")
    parser.add_option("-r", "--resume",
        action="store_true", dest="resume", default=False,
        help="Resume a download")
    parser.add_option("-l", "--live",
        action="store_true", dest="live", default=False,
        help="Enable for live streams")
    parser.add_option("-s", "--silent",
        action="store_true", dest="silent", default=False)
    parser.add_option("-q", "--quality",
        metavar="quality", help="Choose what format to download.\nIt will download the best format by default")
    parser.add_option("-H", "--hls",
        action="store_true", dest="hls", default=False)
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")

    setup_log(options.silent)

    url = args[0]
    get_media(url, options)

if __name__ == "__main__":
    main()
