#!/bin/bash
#first arg = the name of the firewall, second is the port to open
#get my current ip
touch /tmp/updated_firewall
ip=`curl --silent https://api.myip.com | jq -r .ip`
echo $ip
#get the ID of the named firewall
id=`doctl compute firewall list -o json | jq -r '.[] | select (.name =="'$1'") | .id'`
echo $id
#get the droplets the firewall applies to
droplets=`doctl compute firewall list -o json | jq -r '.[] | select (.id == "'$id'") | .droplet_ids | .[]' | paste -sd,`
echo $droplets
#contruct the firewall update and execute
doctl compute firewall update $id --inbound-rules protocol:tcp,ports:$2,address:$ip --name $1  --droplet-ids $droplets

