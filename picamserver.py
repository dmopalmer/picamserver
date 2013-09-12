#! /usr/bin/env python3

"""
picamserver.py

Raspberry Pi camera server for exposing camera module over http.

(c) David Palmer
This code licensed under GPLv2
Started 2013-09-11

A similar project is BerryCam from fotosynlabs, which talks to
an iPad Application.  See
https://bitbucket.org/fotosyn/fotosynlabs.git

"""

from __future__ import print_function

import logging
logging.basicConfig(level=logging.DEBUG)

import sys
import os
import argparse
import re
import subprocess
if sys.version_info.major == 2 :
    logging.warning("Python 3 is prefered for this program")
    import urlparse
    import SimpleHTTPServer as httpserver
    import SocketServer as socketserver
else :
    import urllib.parse as urlparse
    import http.server as httpserver
    import socketserver


defaultPort = 8001  # Change here or use the --port argument

class PiCamHandler(httpserver.SimpleHTTPRequestHandler):
    raspiPath = "/usr/bin/raspistill"
    shortargs = ['?', 'w', 'h', 'q', 'r', 'l', 
                'v', 't', 'th', 'd', 'e', 'x', 
                'tl', 'op', # 'fp', 'p', 'f',
                'n', 'sh', 'co', 'br', 'sa', 
                'ISO', 'vs', 'ev', 'ex', 'awb', 
                'ifx', 'cfx', 'mm', 'rot', 'hf', 'vf', 'roi']
    longargs = ['help', 'width', 'height', 'quality', 'raw', 'latest', 
                'verbose', 'timeout', 'thumb', 'demo', 'encoding', 'exif', 
                'timelapse', 'opacity', #  'fullpreview', 'preview', 'fullscreen',
                'nopreview', 'sharpness', 'contrast', 'brightness', 'saturation', 
                'ISO', 'vstab', 'ev', 'exposure', 'awb', 
                'imxfx', 'colfx', 'metering', 'rotation', 'hflip', 'vflip', 'roi']
    def do_GET(self) :
        logging.info("GET request: %s" % (self.path,))
        parsedParams = urlparse.urlparse(self.path)
        queryParsed = urlparse.parse_qs(parsedParams.query)
        logging.debug("parsedParams: %s" % (parsedParams,))
        logging.debug("queryParsed: %s" % (queryParsed,))
        if parsedParams.path == "/camera" :
            image,self.diagnostic = self.runCommand(queryParsed)
            self.send_response(200)
            self.send_header("Content-type", "image/jpeg")
            self.send_header("Content-length", len(image))
            self.end_headers()
            self.wfile.write(image)
            # self.wfile.close()
            # self.wfile.write(str(queryParsed).encode("utf-8"))
            # self.wfile.write()
        else :
            self.send_error(501,"Only /camera request is supported now")

    def runCommand(self, queryParsed) :
        """From the parsed params, make and execute the RaspiStill command line"""
        # First strip out the output files
        outfiles = []
        for argname in ['-o','--output','-l','--latest'] :
            if argname in queryParsed :
                outfiles += queryParsed.pop(argname)
        for anoutfile in outfiles :
            self.sanitizeFile(anoutfile)
        # FIXME handle the output file case
        cmd = [self.raspiPath,"--timeout","500","--nopreview","--output","-"]
        residual_args = {}
        for p,value in queryParsed.items() :
            if p in self.shortargs :
                cmd += ['-'+p] + value
            elif p in self.longargs :
                # FIXME make it match unique prefixes (or don't bother)
                cmd += ['--'+p] + value
            else :
                residual_args[p] = value
        logging.info("Raspistill command is broken down as %s" % (cmd,))
        # FIXME doesn't return verbose output and other diagnostics yet
        image = subprocess.check_output(cmd,stderr=sys.stderr)
        return (image,"unused args: %s" % (residual_args,)) 
        
                
    def sanitizeFile(self, filename) :
        """Make sure the filename isn't toxic"""
        if re.findall("(\.\.)|(^~)",filename) :
            logging.critical("IP : %s tried to write to file %s.\n" 
                            "Full GET: %s\n"
                            "I no longer feel safe and am shutting down." 
                                % (self.client_address[0], filename,self.path))
            raise RuntimeError("Attempted file system violation")
    
def main(argv) :
    httpd = socketserver.TCPServer(("", defaultPort), PiCamHandler)
    logging.info("picamserver -- Listening on port %d", defaultPort)
    httpd.serve_forever()



if __name__ == "__main__" :
    main(sys.argv)
