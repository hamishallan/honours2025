#!/bin/bash

PASSWORD="honours2025"

sshpass -p "$PASSWORD" scp "/Users/hamish/Documents/UNI 2025/Honours/application/aodaq/client/AoDAQClient.py" honours2025@honours-pi.local:~/project/aodaq_automation/

sshpass -p "$PASSWORD" scp "/Users/hamish/Documents/UNI 2025/Honours/application/aodaq/client/automate_aodaq.py" honours2025@honours-pi.local:~/project/aodaq_automation/

sshpass -p "$PASSWORD" scp "/Users/hamish/Documents/UNI 2025/Honours/application/aodaq/client/calibration.py" honours2025@honours-pi.local:~/project/aodaq_automation/

sshpass -p "$PASSWORD" scp "/Users/hamish/Documents/UNI 2025/Honours/application/aodaq/client/stream_aodaq.py" honours2025@honours-pi.local:~/project/aodaq_automation/

sshpass -p "$PASSWORD" scp "/Users/hamish/Documents/UNI 2025/Honours/application/aodaq/client/controller.py" honours2025@honours-pi.local:~/project/aodaq_automation/
