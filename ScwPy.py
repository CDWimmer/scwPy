# Management for Scaleway servers

from scaleway.apis import ComputeAPI

version = "0.1.0"
# TODO: Separate classes into their own files?
# TODO: make all classes consistent in how they obtain info.
#  e.g. Server.get_ip(), using IDs instead of matching up addresses. declare Server.ip_ID etc. in __init__.
#  This is required for Volumes as the only reliable identifiers are IDs.


class Manager:
    """
    Root of all evil. Instances of Server, IP, etc. should all be created and referenced using commands here.
    """
    def __init__(self, auth_id, organization_id, region):
        self.api = ComputeAPI(region=region, auth_token=auth_id)
        self.org_id = organization_id
        self.servers = set()
        self.ips = set()
        self.volumes = set()
        self.build_ip_list()
        self.build_server_list()
        self.build_volume_list()

    def build_server_list(self):
        """
        Repopulate the set of Server instances. Will destroy any existing set and all references to it,
        reloading information from the Scaleway API. Accessible from Manager.servers
        """

        self.servers = set()
        servers_dict = self.api.query().servers.get()["servers"]
        for server in servers_dict:
            self.servers.add(Server(self, server))

    def build_ip_list(self):
        """
        Repopulate the set of IP instances. Will destroy any existing set and all references to it,
        reloading information from the Scaleway API. Accessible from Manager.ips
        """
        self.ips = set()
        ips_dict = self.api.query().ips().get()
        for ip in ips_dict['ips']:
            self.ips.add(IP(self, ip))

    def build_volume_list(self):
        """
        Repopulate the set of Volume instances. Will destroy any existing set and all reference to it,
        reloading information from the Scaleway API. Accessible from Manager.volumes
        """
        self.volumes = set()
        volumes_dict = self.api.query().volumes().get()
        for volume in volumes_dict["volumes"]:
            self.volumes.add(Volume(self, volume))

    def get_server_by_name(self, name: str):
        for server in self.servers:
            if server.name == name:
                return server
        raise LookupError("No server with that name found!")

    def get_server_by_id(self, id_str: str):
        for server in self.servers:
            if server.id == id_str:
                return server
            raise LookupError("No server with that ID found!")

    def get_ip_by_id(self, id_str: str):
        """
        Obtain an IP from a known ID string.
        """
        for ip in self.ips:
            if id_str == ip.id:
                return ip
        raise LookupError("No IP with that ID found!")

    def get_ip_by_address(self, address: str):
        """
        Obtain an IP from a known public address.
        """
        for ip in self.ips:
            if address == ip.address:
                return ip
        raise LookupError("No IP with that address found!")

    def new_ip(self):
        """Creates a brand new IP through the Scaleway API and creates an associated IP instance.
        Returns that instance."""
        result = self.api.query().ips.post({"organization": self.org_id})['ip']
        print(result)
        new_ip = IP(self, result)
        self.ips.add(new_ip)
        return new_ip


class IP:
    """A class to hold information and functions pertaining to a Scaleway IP object."""
    def __init__(self, manager, dict_info):
        self.manager = manager
        self.address = dict_info["address"]
        self.id = dict_info["id"]
        # Check if `server` is set to None, if not then pull out the id of the server we're attached to:
        if dict_info["server"] is None:
            self.server_id = None
        else:
            self.server_id = dict_info['server']['id']

    def get_server(self):
        """
        Returns an instance of Server for the server associated with this IP, if attached to one.
        Otherwise returns None
        :rtype: 'Server'
        """
        if self.server is None:  # TODO: Rewrite this to use IDs or something?
            return Empty()
        for ip in self.manager.ips:
            if ip.address == self.address:
                return ip
        return None  # line should only be reached if above 'if' never came True.

    def delete(self):
        """
        Deletes the IP from your Scaleway account and removes this instance from the Manager.ips list.
        Cannot be undone.
        """
        print("Deleted", self.address)
        result = self.manager.api.query().ips(self.id).delete()
        self.manager.ips.remove(self)
        # TODO: Figure out something more useful to return?
        return result

    def __str__(self):
        return f"{self.address}"


class Server:
    """
    A class to hold information and functions pertaining to a Scaleway Server instance
    """
    def __init__(self, manager, dict_info):
        self.manager = manager
        self.name = dict_info["name"]
        self.id = dict_info["id"]
        self.state = dict_info["state"]
        self.state_detail = dict_info["state_detail"]
        # Check if `public_ip` is set to None, if not then pull out our address:
        if dict_info["public_ip"] is None:
            self.address = None
        else:
            self.address = dict_info["public_ip"]["address"]
            self.ip_id = dict_info["public_ip"]["id"]
        self.private_ip = dict_info["private_ip"]

    def get_ip(self):
        """Return an instance of IP for the address that's associated with this server, if one is attached.
        Otherwise returns None.
        :rtype: 'IP'
        """
        if self.address is None:
            return Empty()
        else:
            for ip in self.manager.ips:
                if ip.address == self.address:
                    return ip
        return Empty()  # line should not be reached

    def volumes(self):
        """Returns a set of instances of Volume for all the drives attached to this server."""
        raise NotImplemented("I haven't gotten around to this yet :(")

    def power_on(self):
        """Put the plug back in. Does not update state. Use Server.check_state for that"""
        result = self.manager.api.query().servers(self.id).action.post({"action": "poweron"})
        return result

    def power_off(self):
        """Pull the plug on a server."""
        result = self.manager.api.query().servers(self.id).action.post({"action": "poweroff"})
        return result

    def attach_ip(self, ip: 'IP'):
        """Attaches the given IP instances to this server"""
        result = self.manager.api.query().ips(ip.id).patch({"server": self.id})
        return result

    def detach_ip(self):
        """Remove the IP attached to the server."""
        result = self.manager.api.query().ips(self.ip().id).patch({"server": None})

    def update_state(self):
        """TODO: Update the state and other parameters of this instance from the API without recreating the instance"""
        pass


class Volume:
    """
    A class to hold information and functions pertaining to a Scaleway Volume.
    """
    def __init__(self, manager, volume_dict):
        # TODO: more... stuff?
        self.manager = manager
        self.name = volume_dict["name"]
        self.id = volume_dict["id"]
        self.volume_type = volume_dict["volume_type"]
        if volume_dict["server"] is not None:
            self.server_id = volume_dict["server"]["id"]
        else:
            self.server_id = None

    def get_server(self):  # This'll have to be done using IDs, same should be applied to other object types
        if self.server_id is None:
            return Empty()
        else:
            for server in self.manager.servers:
                if server.id == self.server_id:
                    return server
        return Empty()  # line should not be reached


class Empty:
    """
    Class to be returned when nothing relevant is found for a call.
    Returns `None` for nearly all attributes.
    """

    def return_none(self, *args, **kwargs):
        return None

    def __getattr__(self, item):
        return self.return_none()

    def __repr__(self):
        return None

    def __str__(self):
        return None
