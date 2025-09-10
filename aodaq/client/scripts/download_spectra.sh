#!/bin/bash

PASSWORD="honours2025"

sshpass -p "$PASSWORD" scp honours2025@honours-pi.local:~/project/aodaq_automation/spectra.db "/Users/hamish/Documents/UNI 2025/Honours/application/aodaq/client/database"
