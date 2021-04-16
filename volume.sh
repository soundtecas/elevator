#!/bin/sh
amixer sset Master 0
/usr/local/bin/dsptoolkit install-profile /home/pi/elevator/dsp.xml && amixer sset DSPVolume '20%' && amixer sset Master '100%' alsactl store