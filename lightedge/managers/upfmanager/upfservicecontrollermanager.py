from empower_core.service import EService

# from empower_core.envmanager.envmanager.env import Env

import tornado
from tornado.web import Application
from tornado.ioloop import IOLoop

import copy

from threading import Lock
from threading import Timer

from lightedge.managers.upfmanager.match import Match

from lightedge.managers.upfmanager.matchmaphandler import MatchMapHandler
from lightedge.managers.upfmanager.uemaphandler import UEMapHandler
from lightedge.managers.upfmanager.upfclienthandler import UPFClientHandler

from lightedge.managers.upfmanager.dictionarywrapper import *

from pymodm.errors import ValidationError
from lightedge.managers.upfmanager.upfservicecontrollerwshandler import UPFServiceControllerWSHandler

from pprint import pformat

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 7000

class MatchList(list):

    def _update_index(self):

        print("Updating indexes")

        for match in self:
            match.delete()

        new_index = 0
        for match in self:
            match.index = new_index
            match.save()
            new_index += 1

    def insert(self, index, match):

        print("Inserting  ", match, " at ", index)

        super().insert(index, match)

        self._update_index()

    def pop(self, index: int = -1):

        self[index].delete()
        super().pop(index)

        self._update_index()

    def clear(self):

        print("Clearing...")

        for match in self:
            print("Deleting ", match)
            match.delete()
        super().clear()

    def get_match_index(self, match):

        return match.index

    def _fill_from_list(self, matches):
        matches.sort(key=self.get_match_index)
        self.clear()
        for match in matches:
            self.insert(match.index, match)
            # match = match.to_dict()
            # print ("MATCH: %s", match)
        
class UPFServiceControllerManager(EService):
    """Service exposing the UPF Service Controller

    Parameters:
        host: the name/IP address of the hosting device
        port: the port on which the Controller should listen for websocket 
            communication (optional, default: 7000)
    """

    HANDLERS = [MatchMapHandler, UEMapHandler, UPFClientHandler]

    def __init__(self, context, service_id, host, port):

        super().__init__(context=context, service_id=service_id, port=port)

        self.db_lock = Lock()

        # self.remove_all_matches_from_db()

        self.matches = MatchList()

        self.import_db_matches()

        # self.test_match_op()

        for match in self.matches:
            match = match.to_dict()
            self.log.info("MATCH: %s", match)

        self.upf_client_handlers = {}

        settings = {
            "trigger_upf_client_init": self.trigger_upf_client_init,
            "leave_manager": self.remove_upf_client
        }

        # print(settings)

        self.application = Application([(r"/", UPFServiceControllerWSHandler,
                                        settings)])

        self.application.listen(self.port)

        self.upf_request_validator = UPFRestRequestValidator(self.matches)

    @property
    def host(self):
        """Return host."""

        return self.params["host"]

    @host.setter
    def host(self, value):
        """Set host."""

        self.params["host"] = value

    @property
    def port(self):
        """Return port."""

        return self.params["port"]

    @port.setter
    def port(self, value):
        """Set port."""

        if "port" in self.params and self.params["port"]:
            raise ValueError("Param port can not be changed")

        self.params["port"] = int(value)

    def _get_db_matches(self):
        self.log.info("Importing db-stored matches")
        all_matches = Match.objects.all()
        matches = []
        for match in all_matches:
            matches.append(match)
        return matches

    def import_db_matches(self):
        self.lock_db()
        self.matches._fill_from_list(self._get_db_matches())
        self.unlock_db()

    def lock_db(self):
        # self.log.debug("DB LOCKED")
        self.db_lock.acquire()

    def unlock_db(self):
        self.db_lock.release()
        # self.log.debug("DB UNLOCKED")

    def get_upf_client_by_id(self, client_id):
        if client_id in self.upf_client_handlers:
            return self.upf_client_handlers[client_id]
        return None

    def add_upf_client(self, client, overwrite=True):
        client_id = client.get_params__id()
        if client_id in self.upf_client_handlers:
            self.log.warning("UPF Client Handler with id %s is already present",
                             client_id)
            if overwrite:
                self.log.warning("OVERWRITING UPF Client id %s",
                                 client_id)
            else:
                self.log.warning("KEEPING old UPF Client id %s",
                                 client_id)
            return False
        
        self.upf_client_handlers[client_id] = client
        self.log.info("ADDED NEW UPF Client Handler with id %s", client_id)
        self.log.info("UPF Client Handlers: \n%s", 
                      pformat(self.upf_client_handlers))
        return True

    def remove_upf_client(self, client=None, client_id=None, 
                          missing_tolerant=True):
        if client is not None:
            client_id = client.get_params__id()
        if client_id is None:
            self.log.warning("UPF Client Handler with id %s is NOT present",
                             client_id)
            if missing_tolerant:
                return True
            
            return False
        
        del self.upf_client_handlers[client_id]
        self.log.info("UPF Client Handlers: \n%s", self.upf_client_handlers)
        return True

    def rest__get_matchmap(self, match_index):

        # self.log.debug("rest__get_matchmap")
        
        self.upf_request_validator.get_matchmap(match_index)

        if match_index != -1:
            return self.matches[match_index]

        return self.matches

    def rest__get_matchmap_checked(self):
        self.upf_request_validator.get_matchmap(-1)

        result = {}

        result["matches"] = []
        for key in self.matches:
            result["matches"]= self.matches
        main_matches = result["matches"]

        result["missing_match"] = False
        result["extra_match"] = False
        result["messed_match"] = False
        
        for key in self.upf_client_handlers:
            local_matches = self.upf_client_handlers[key]._local_matches
            if (len(main_matches) > len(local_matches)):
                result['missing_match'] = True
            elif (len(main_matches) < len(local_matches)):
                result['extra_match'] = True
            else:
                for index in range(len(main_matches)):
                    # self.log.info(index)
                    if main_matches[index] != local_matches[index]:
                        result["messed_match"] = True
        
        return result


    def rest__add_matchmap(self, match_index, data):
        """Set matchmap."""

        # if isinstance(data, Match):
        #     match = data
        # else:
        #     match = Match()
        #     match.from_dict(match_index, data)

        self.upf_request_validator.post_matchmap(match_index, data)
        
        match = Match()
        match.from_dict(match_index, data)

        # if match.index not in range(0, len(self.matches) + 1):
        #     raise ValueError("Indexes must be within 1 and %s"
        #                      % (len(self.matches) + 1))

        # if (match.dst_port != 0 or match.new_dst_port != 0) \
        #         and match.ip_proto_num not in self._prot_port_supp:
        #     raise ValueError("Matching protocol does not allow ports")

        self.matches.insert(match.index, match)

        data = match.to_dict()
        self.send_matchop_to_all_clients(MSG_TYPE__MATCH_ADD,
                                         match_index,
                                         data)
        

    def rest__del_matchmap(self, match_index):
        """Delete a match rule."""

        self.upf_request_validator.delete_matchmap(match_index)

        # self.log.debug("del_matchmap %s", match_index)

        # if match_index != -1:
        #     if match_index >= 0:
        #         try:
        #             self.matches.pop(match_index)
        #             self.send_matchop_to_all_clients(MSG_TYPE__MATCH_DELETE,
        #                                              match_index)
        #         except:
        #             raise ValueError("Index %i is not present in match table"
        #                              % match_index)
        #     else:
        #         raise ValueError("Index has to be greater than 0")
        # else:
        #     self.matches.clear()
        #     self.send_matchop_to_all_clients(MSG_TYPE__MATCH_DELETE,
        #                                      MATCH_DELETE_MSG_VALUE__DELETE_ALL)

        if match_index >= 0:
            
            self.send_matchop_to_all_clients(MSG_TYPE__MATCH_DELETE,
                                                match_index)
            self.matches.pop(match_index)
        else:
            self.matches.clear()
            self.send_matchop_to_all_clients(MSG_TYPE__MATCH_DELETE,
                                            MATCH_DELETE_MSG_VALUE__DELETE_ALL)
            
    def rest__get_uemap(self, ue_ip=None):
        """Return UE Map."""

        ue_map = {}

        for key in self.upf_client_handlers:
            if ue_ip is None:
                ue_map[key] = self.upf_client_handlers[key].get_params__ue_map()
            else:
                self.log.warning("SPECIFIC UE_IP case NOT YET HANDLED PROPERLY")
                ue_map[key] = self.upf_client_handlers[key].get_params__ue_map()

        return ue_map

    def rest__get_upf_clients(self):
        """Return UPF Clients"""

        main_matches = ""
        
        for i in range(len(self.matches)):
            main_matches = main_matches + self.matches[i].to_str_with_desc()

        upf_clients = {}

        for key in self.upf_client_handlers:
            upf_clients[key] = self.upf_client_handlers[key].get_descriptor()
            # local_matches = ""
            # for i in range(len(upf_clients[key]["local_matches"])):
            #     local_matches =\
            #         local_matches + upf_clients[key]["local_matches"][i]
            upf_clients[key]["status"] = "inconsistent"
            if main_matches == upf_clients[key]["stringified"]:
                upf_clients[key]["status"] = "consistent"
            del upf_clients[key]["stringified"]
            
        return upf_clients

    def send_matchop_to_all_clients(self, request_type, index=None, data={}):

        match_op = self.format_matchop_for_clients(request_type, index, data)

        if match_op is None:
            self.log.warning("MATCH OP forwarding aborted (type=%s)",
                             request_type)
            return

        for key in self.upf_client_handlers:
            client = self.upf_client_handlers[key]
            self.log.debug(
                "MATCH REQUEST (type=%s) ADDED to Client Handler %s OP Queue", 
                request_type,
                str(client.get_params__id()))
            client.push_matchop(copy.deepcopy(match_op))
            client.queue_check()

    def format_matchop_for_clients(self, request_type, index=None, data={}):

        match_op = None

        if request_type == MSG_TYPE__MATCH_ADD:
            match_op = copy.deepcopy(data)
            match_op["type"] = MSG_TYPE__MATCH_ADD
            if not match_op["index"]:
                if index is None:
                    match_op = None
                else:
                    match_op["index"] = 0

        elif request_type == MSG_TYPE__MATCH_DELETE:
            match_op = {}
            match_op ["type"] = MSG_TYPE__MATCH_DELETE
            uuid = None
            if index is not None:
                uuid = self.matches[index].to_dict()["uuid"]
                # index = MATCH_DELETE_MSG_VALUE__DELETE_ALL
            match_op["match_uuid"] = uuid

        return match_op    

    

    def trigger_upf_client_init(self, client):
        if client is None:
            self.log.warning("UPF Client to be initialized is None")
            return False
        else:
            # self.log.warning("TODO: add UPF_Client Handler stuff")
            try:
                self.lock_db()
                # Push DELETE ALL rules
                client.push_matchop({"type": "match_delete"})
                # Retrive db-stored rules
                # Push rules into UPF Client handler
                for match in self.matches:
                    match = match.to_dict()
                    match["type"] = "match_add"
                    client.push_matchop(match)
                    client.queue_check()
                # Set UE_map to None
                client.set_params__ue_map(None)
                # Add UPF Client handler to upf_client_handlers dict
                self.add_upf_client(client)
                return True
            except Exception as e:
                self.log.error(e)
                client.close()
                return False
            finally:
                self.unlock_db()

    def remove_all_matches_from_db(self):
        self.lock_db()
        # self.log.info("\n\nREMOVE ALL: %s", (Match.objects))
        Match.objects.delete()
        self.log.warning("ALL MATCHES in DB DELETED")
        self.log.info("Matches after deletion: %s", list(Match.objects))
        # Match.deleteMany({}, self.unlock_db)
        self.unlock_db()

    def test_match_op(self):
        self.log.info("\n\ntest_match_op START\n")
        
        # self.matches.refresh()

        # self.del_matchmap(-1)

        data = {     
            "ip_proto_num": 6,
            "desc": "This is just a test 0!",
            "dst_ip":
                "127.0.0.1",
            "netmask": 32,
            "dst_port": 0,
            "new_dst_ip": "127.0.0.1",
            "new_dst_port": 0
        }

        # self.add_matchmap(0,data)

        data = {     
            "ip_proto_num": 6,
            "desc": "This is just a test 1!",
            "dst_ip":
                "127.0.0.1",
            "netmask": 32,
            "dst_port": 1,
            "new_dst_ip": "127.0.0.1",
            "new_dst_port": 1
        }

        # self.add_matchmap(1,data)

        data = {     
            "ip_proto_num": 6,
            "desc": "This is just a test 2!",
            "dst_ip":
                "127.0.0.1",
            "netmask": 32,
            "dst_port": 2,
            "new_dst_ip": "127.0.0.1",
            "new_dst_port": 2
        }

        # self.add_matchmap(0,data)

        data = {     
            "ip_proto_num": 6,
            "desc": "This is just a test 3!",
            "dst_ip":
                "127.0.0.1",
            "netmask": 32,
            "dst_port": 3,
            "new_dst_ip": "127.0.0.1",
            "new_dst_port": 3
        }

        # self.add_matchmap(0,data)
        
        data = {    
            "desc": "First",   
            "ip_proto_num": 1,    
            "dst_ip": "2.2.2.2",    
            "netmask": 32,    
            "dst_port": 0,    
            "new_dst_ip": "192.168.0.1",    
            "new_dst_port": 0
        }

        self.add_matchmap(0,data)

        data = {    
            "desc": "Second",   
            "ip_proto_num": 1,    
            "dst_ip": "2.2.2.3",    
            "netmask": 32,    
            "dst_port": 0,    
            "new_dst_ip": "192.168.0.1",    
            "new_dst_port": 0
        }

        self.add_matchmap(0,data)

        # self.del_matchmap(0)

        self.log.info("\n\ntest_match_op END\n")

def launch(context, service_id, host=DEFAULT_HOST, port=DEFAULT_PORT):
    """ Initialize the module. """

    return UPFServiceControllerManager(context=context, service_id=service_id,
                                       host=host, port=port)

class UPFRestRequestValidator():

    def __init__(self, match_list):
        self.match_list = match_list

        self._prot_port_supp = {6: "tcp", 17: "udp", 132: "sctp"}

    def get_matchmap(self, match_index):

        match_index = int (match_index)

        if match_index == -1: # get ALL matches
            return True
        
        if match_index <= -1: # Invalid NEGATIVE Index
            message = "Invalid match index '%i': must be greater than 0"\
                        % (match_index + 1)
            raise ValueError(message)
        
        matches_length = len(self.match_list)

        if matches_length == 0: # VOID match list
            message = "Invalid match index '%i': match list is void"\
                        % (match_index + 1)
            raise ValueError(message)

        elif (match_index + 1) > matches_length: # Invalid TOO LARGE index
            message = "Invalid match index '%i': acceptable range is [1, %i]"\
                        % (match_index + 1, matches_length )
            raise ValueError(message)
        
        return True

    def post_matchmap(self, match_index, match_data):
        if match_index:
            match_index = int (match_index + 1)

            if match_index <= 1:
                message = "Invalid match index '%i': must be greater than 0"\
                          % (match_index)
                raise ValueError(message)

            matches_length = len(self.match_list)
            if matches_length == 0:
                if match_index != 1:
                    message =\
                        "Match list is void: inserting match index has to be 1"
                    raise ValueError(message)

            elif match_index > (matches_length + 1):
                message = "Invalid match index '%i': acceptable range is [1, %i]"\
                          % (match_index , (matches_length + 1) )
                raise ValueError(message)
        
        if (int(match_data["dst_port"]) < 0 or int(match_data["new_dst_port"]) < 0):
            raise ValueError("dst_port and new_dst_port shall be both non-negative")

        match = None
        try:
            match = Match()
            match.from_dict(match_index, match_data)
        except Exception as e:
            raise ValueError(str(e))
        
        if (match.dst_port != 0 and match.new_dst_port == 0) \
            or (match.dst_port == 0 and match.new_dst_port != 0):
            raise ValueError("When rewriting, dst_port and new_dst_port shall be both 0 or !=0")

        if (match.dst_port != 0 or match.new_dst_port != 0) \
                and match.ip_proto_num not in self._prot_port_supp:
            raise ValueError("Matching protocol '%i' does not allow ports"\
                             % (match.ip_proto_num))

        for stored_match in self.match_list:
            if match == stored_match:
                message = "New match is already present in match table at index %i"\
                            % (stored_match.index + 1)
                raise ValueError(message)  

        return True

    def delete_matchmap(self, match_index):
        match_index = match_index + 1
        if match_index != 0:
            if match_index >= 0:
                if match_index > len(self.match_list):
                # try:
                #     print ("match_index: %i", match_index)
                #     matches_length = len(self.match_list)
                #     print ("matches length: %i", matches_length)
                #     self.match_list.pop(match_index)
                #     self.send_matchop_to_all_clients(MSG_TYPE__MATCH_DELETE,
                #                                      match_index)
                # except Exception as e:
                #     print(e)
                    raise ValueError("Index %i is not present in match table"
                                     % match_index)
            else:
                raise ValueError("Index has to be greater than 0")
        return True