# Management for Scaleway servers

from scaleway.apis import ComputeAPI


class Manager:
    """
    Root of all evil. Instances of Server, IP, etc. should all be created and referenced using commands here.
    """
    def __init__(self, auth_id, organization_id, region):
        self.api = ComputeAPI(region=region, auth_token=auth_id)
        self.org_id = organization_id
        self.servers = []
        self.ips = []
        self.volumes = []
        self.build_ip_list()
        self.build_server_list()

    def build_server_list(self):
        """
        Repopulate the list of Server instances. Will destroy any existing list and all references to it,
        reloading information from the Scaleway API. Accessible from Manager.servers
        """

        self.servers = []
        servers_dict = self.api.query().servers.get()["servers"]
        for server in servers_dict:
            self.servers.append(Server(self, server))

    def build_ip_list(self):
        """
        Repopulate the list of IP instances. Will destroy any existing list and all references to it,
        reloading information from the Scaleway API. Accessible from Manager.ips
        """
        ips_dict = self.api.query().ips().get()
        for ip in ips_dict['ips']:
            self.ips.append(IP(self, ip))

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
        # TODO
        raise NotImplemented

    def get_ip_by_address(self, address: str):
        # TODO
        raise NotImplemented

    def new_ip(self):
        """Creates a brand new IP through the Scaleway API and creates an associated IP instance.
        Returns that instance."""
        result = self.api.query().ips.post({"organization": self.org_id})['ip']
        print(result)
        new_ip = IP(self, result)
        self.ips.append(new_ip)
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

    def server(self):
        """
        Returns an instance of Server for the server associated with this IP, if attached to one.
        Otherwise returns None
        :rtype: 'Server'
        """
        if self.server is None:
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
        result = self.manager.api.query().ips(self.id).delete()
        self.manager.ips.remove(self)
        # TODO: Figure out something more useful to return?
        return result

    def __str__(self):
        return f"{self.address}"


class Server:
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

    def ip(self):
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
        return Empty  # line should not be reached

    def volumes(self):
        """Returns a list of instances of Volume for all the drives attached to this server."""
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
    def __init__(self):
        # TODO: storage objects
        raise NotImplemented("Storage objects not yet done.")


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
