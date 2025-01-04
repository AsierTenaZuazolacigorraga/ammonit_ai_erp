# Next set the the IPv4 address, you will need to substitute your configuration name and IPv4 address in CIDR notation in this command:
# sudo nmcli con mod <configuration name> ipv4.addresses <ip address>. So I would run
sudo nmcli con mod "Wired connection 1" ipv4.addresses 10.0.0.9/24

# Next set the IPv4 gateway, for a lot of people, this will be the IP address of your router
sudo nmcli con mod "Wired connection 1" ipv4.gateway 10.0.0.1

# Next set the DNS, again, you could use your router but you could also use another like 8.8.8.8
sudo nmcli con mod "Wired connection 1" ipv4.dns 10.0.0.1

# Next set the addressing from DHCP to static
sudo nmcli con mod "Wired connection 1" ipv4.method manual

# Make sure the default gateway does not override the wifi
sudo nmcli con mod "Wired connection 1" ipv4.route-metric 700

# Restart the connection to pick up these changes
sudo nmcli con up "Wired connection 1"