# palo-alto-nautobot

Repository for ideas behind using Nautobot as a way to manage firewall policies for Palo Alto Firewalls

capirca-policy
-------------------
Use capirca integration in Nautobot firewall models to deploy policies
Must specify Nautobot Server parameters via environmental variables
- NAUTOBOT_SERVER - for the ip/hostname and port number used for nautobot
- NAUTOBOT_TOKEN - the token needed to read data from nautobot

Workflow 
- Send in a partial configuration to the device and perform a replace function
- Commit the configuration

Caveats: 
- Need to generate zone information with a config context(example: zone-config-context.yaml)

inventory.yaml
-------------------
Works similiarly to Nornir inventory (TODO: Use Nornir + Nautobot Inventory integration)
Parameters that must be defined:
- Hostname (Connecting to device and for Nautobot lookup)
- Key (XML-API key for Palo Alto Device)

