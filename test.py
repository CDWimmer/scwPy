import ScwPy
import time


with open("real_org.id", "r") as org_file:
    org = org_file.read()

with open("real.key", "r") as key_file:
    key = key_file.read()
fr_manager = ScwPy.Manager(key, org, "par1")

# print some information about all of our servers:
for server in fr_manager.servers:
    print(f"Server name: {server.name} | Server ID: {server.id}\n"
          f"Address: {server.address} | IP ID: {server.get_ip().id}\n"
          f"=============================================")

# Create a new IP
new_ip = fr_manager.new_ip()

# "scw-openVPN" is the name of a server on my account, currently offline and without IP.
target = fr_manager.get_server_by_name("scw-openVPN")

# attach our fresh IP to the chosen server
target.attach_ip(new_ip)

# turn on the server
target.power_on()

# wait naively and hope the server turns on in under 2 minutes
time.sleep(120)

# turn off the server
target.power_off()

# remove the IP
target.detach_ip()
# Note that the website UI will show "IP Address" as its private IP until it actually shuts down

# delete the IP we created at the beginning
new_ip.delete()


