# Management for Scaleway servers

from scaleway.apis import ComputeAPI

ORG_ID = "75536117-245b-4a47-a82f-4e5c74ae4793"

api = ComputeAPI(region='par1', auth_token='16624bda-22f2-485e-8465-97192967993e')

all_srv = api.query().servers.get()["servers"]


# dict_keys(['allowed_actions', 'maintenances', 'state_detail', 'image', 'creation_date', 'public_ip', 'private_ip',
# 'id', 'dynamic_ip_required', 'modification_date', 'enable_ipv6', 'hostname', 'state', 'bootscript', 'location',
# 'boot_type', 'ipv6', 'commercial_type', 'tags', 'arch', 'extra_networks', 'compute_cluster', 'name', 'protected',
# 'volumes', 'security_group', 'organization'])


def show_detail(server_id: str = None):
    """Print basic details of server given an id, or all servers if no id given."""

    def __print_srv__(target_srv):
        print(target_srv["hostname"] + " @ " + target_srv["public_ip"]["address"])
        print(target_srv["id"])
        print(target_srv["state_detail"])
        print("actions:", target_srv["allowed_actions"])
        print("#####")

    if id is not None:
        for srv in all_srv:
            __print_srv__(srv)
    else:
        srv = api.query().servers(server_id).get()
        __print_srv__(srv)


def del_ip(ip_id: str):
    """delete a reserve IP given its id."""
    result = api.query().ips(ip_id).delete()
    return result


def create_ip():
    """Create a new reserved IP and return a dict of its information."""
    result = api.query().ips.post({"organization": ORG_ID})
    return result["ip"]


def power_off(server_id: str):
    """Pull the plug on a server."""
    result = api.query().servers(server_id).action.post({"action": "poweroff"})
    return result


def power_on(server_id: str):
    """Put the plug back in."""
    result = api.query().servers(server_id).action.post({"action": "poweron"})
    return result


all_ips = api.query().ips.get()

new_ip = create_ip()

print(new_ip)

del_ip(new_ip["id"])
