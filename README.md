PiCamServer
===========

Use your web browser to control and view your Raspberry Pi camera from a remote machine.

Raspberry Pi Camera exposed to IP for use on the web.

Inspired, but not sharing significant code with, 
<a HREF="https://bitbucket.org/fotosyn/fotosynlabs.git">BerryCam.py</a>

Run picamserver.py from a terminal.

To have the camera take a picture and display it in your browser (or e.g. use wget 
to store it on your local disk) use a URL like:
<http://192.168.0.45:8001/camera?width=1600&height=1200>
replacing 192.168.0.45 with the IP number or name of your Raspberry Pi.  
Arguments to pass to raspistill (which must be installed and functional on your pi)
are given as the above shows for --width and --height.  
Flags that don't take an argument value (e.g. --raw, --nopreview) should be given a value of 0 or 1 to enable or disable.

The URL <http://192.168.0.45:8001> brings up an auto-refreshing picture with some input fields to control from your browser.
