#!/bin/bash

rm ~/.ssh/known_hosts
read -s -p "Pass: " passW
printf "\n"
while read -r line
do
    echo "running $line"
    sshpass -p $passW ssh -o "StrictHostKeyChecking no" research@$line 'sudo docker rmi $(sudo docker images -a -q) -f'
done < "lab.txt"
