# RFID Dorm Lock System using Student IDs
Easily mountable lock to unlock dorm room door.

## Tech Stack
- Raspberry Pi (Raspbian OS)
- SSH, scp
- Linux CLI & systemd
- Static IP configuration (dhcpcd.conf / /etc/network/interfaces)
- Network administration (university DHCP/static IP request process)

## Features
- Add/Remove new ID remotely/locally
- Automatic locking after custom time interval

## How To Run
- Connect Proxmarx RFID reader to Pi
- run server.py on local computer
- run client.py on Pi
