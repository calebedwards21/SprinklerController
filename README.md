# SprinklerController
NOTE: Must clone repo in PI users home directory (pi@raspberrypi:~$) EXAMPLE: /home/pi/SprinklerController

Setting up SIP to automatically execute on reboot 

 1.) Copy Script file sip.service to /etc/systemd/system. Run command:
     sudo cp SprinklerController/SIP/sip.service /etc/systemd/system/
     
 2.) Enable sip.service. Run command:
     sudo systemctl enable sip.service
     
 3.) Reboot PI. Run command:
     sudo reboot

Check status,start,stop and restart SIP Interface with terminal commands:

- Disable auto-start: sudo systemctl disable sip.service
 
- Status: systemctl status sip
 
- Start: sudo systemctl start sip
 
- Stop: sudo systemctl stop sip
 
- Restart: sudo systemctl restart sip

