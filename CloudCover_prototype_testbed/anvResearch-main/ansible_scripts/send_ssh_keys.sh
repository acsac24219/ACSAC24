#!/bin/bash

rm ~/.ssh/known_hosts
read -s -p "Pass: " passW
printf "\n"
while read -r line
do
    echo "running $line"
    sshpass -p $passW ssh-copy-id -o "StrictHostKeyChecking no" research@$line 
done < "lab.txt"
