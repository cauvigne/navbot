#!/bin/bash
rsync -avv --exclude={'*.env','.git/','.idea/','temp/','doc/','.gitignore'} . navbotmachine:/usr/share/navbot/
scp prod.env navbotmachine:/usr/share/navbot/.env
ssh nuc "sudo -S systemctl restart navbot.service && sudo -S systemctl status navbot.service"
