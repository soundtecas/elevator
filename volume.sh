#!/bin/sh
/usr/local/bin/dsptoolkit install-profile /home/pi/elevator/dsp.xml && amixer sset DSPVolume '20%' && alsactl store