import ScwPy

with open("real_org.id", "r") as org_file:
    org = org_file.read()

with open("real.key", "r") as key_file:
    key = key_file.read()
fr_manager = ScwPy.Manager(key, org, "par1")


for server in fr_manager.servers:
    print(f"Server name: {server.name} | Server ID: {server.id}\n"
          f"Address: {server.address} | IP ID: {server.ip().id}\n"
          f"=============================================")


# Create a new IP (remember to delete it after testing or you'll be hemorrhaging money)
new_ip = fr_manager.new_ip()

target = fr_manager.get_server_by_name("scw-openVPN")
target.attach_ip(new_ip)
target.power_on()



