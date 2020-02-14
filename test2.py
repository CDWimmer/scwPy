import ScwPy


with open("real_org.id", "r") as org_file:
    org = org_file.read()

with open("real.key", "r") as key_file:
    key = key_file.read()
fr_manager = ScwPy.Manager(key, org, "par1")

# print some information about all of our servers:
print("\n\n============== Servers ==============\n")
for server in fr_manager.servers:
    print(f"{server.name} | {server.state} | ID: {server.id}\n"
          f"Address: {server.address} | IP ID: {server.get_ip().id}\n"
          f"-------------------------------------------------------")


# info about volumes:
print("\n\n============== Volumes ==============\n")

for volume in fr_manager.volumes:
    print(f"{volume.name} | ID: {volume.id}\n"
          f"Attached to: {volume.get_server().name}\n"
          f"-------------------------------------------------------")


