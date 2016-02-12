# admanager


#run install-admanager.sh

	The script will ask you for a series of variables that you will need to input in order to configure the manager.
	
	#!/usr/bin/env bash

	#This is the AD manager Install and Configuration Script.
	
	#ARGUMENT DESC
	#web_folder_location=/opt/admanager1
	#ad_manager_url=admanager.oneplatform.build:8001
	#admanager_location=/opt/admanager/admanager.py
	#username="ADMIN USERNAME"
	#password="AD PASSWORD"
	#host="AD HOST"
	#port="389"
	#domain="AD Domain"
	
	echo "Type the location of the webserver folder that will host your UI, followed by [ENTER]:"
	
	read web_folder_location
	
	echo "Type the url of the admanager rest interface and port, followed by [ENTER]:"
	
	read ad_manager_url
	
	echo "Type the admin user for active directory, followed by [ENTER]:"
	
	read username
	
	echo "Type the admin passford for active director, followed by [ENTER]:"
	
	read password
	
	echo "Type the host address of active directory, IP, followed by [ENTER]:"
	
	read host
	
	echo "Type the port for active directory usually 389, followed by [ENTER]:"
	
	read port
	
	echo "Type the url of your active directory domain, followed by [ENTER]:"
	
	read domain
	
	echo "Type the location of the active directory manager script admanager.py, followed by [ENTER]:"
	
	read admanager_location
	
	
	if [ -z "$web_folder_location" ]; then
		 
		if [ -z "$web_folder_location" ]; then
		
			echo "Creating ad manager directories."
			
			sudo mkdir /opt/admanager
		
			echo "Installing admanager."
			
			sudo cp ./admanager.py /opt/admanager/admanager.py
		
			echo "Installing Upstart."
			
			sudo cp ./admanager.conf /etc/init/admanager.conf
			
			echo "Creating Log Directory."
			
			sudo mkdir /var/log/adcontrol
			
			echo "Set log directory permissions."
			
			sudo chmod -R 766 /var/log/adcontrol
			
			echo "Move index to web_folder_location."
			
			sudo cp ./index.html $web_folder_location/index.html
			
			echo "Inserting admanger dns name into the index file"
			
			sed -i -e "s/DNSADDRESSMANAGER/$ad_manager_url/" $web_folder_location/index.html 
			
			echo "Setting up AD domain credentials"		
			
			sudo sed -i -e "s/USERNAMESED/$username/" $admanager_location 		
			
			sudo sed -i -e "s/PASSWORDSED/$password/" $admanager_location		
			
			sudo sed -i -e "s/HOSTSED/$host/" $admanager_location	
			
			sudo sed -i -e "s/PORTSED/$port/" $admanager_location	
			
			sudo sed -i -e "s/DOMAINSED/$domain/" $admanager_location	
			
	
		else
		
			echo "Please specify a web folder location to copy the webpage files to."
		
		fi
	
	else
	
		echo "Please specify the dns and port of the admanager for the index file. Example: http://admanager.oneplatform.build:8001"
	
	fi

