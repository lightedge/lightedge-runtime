import uuid
import copy
import time
import json
import uuid
import tornado.web
import tornado.ioloop
import tornado.websocket


MSG_KEY__TYPE = 'type'
MSG_KEY__VERSION = 'version'
MSG_KEY__UUID = "uuid"
MSG_VERSION_VALUE__DEFAULT = 0
MSG_TYPE__HELLO = "hello"
MSG_TYPE__UE_MAP = "ue_map"
MSG_TYPE__MATCH_ACTION_RESULT = "match_action_result"
MSG_TYPE__MATCH_ADD = "match_add"
MSG_TYPE__MATCH_DELETE = "match_delete"

GENERIC_MSG_DESCRIPTOR = {}
def _configure_generic_msg_descriptor():
    gmd = GENERIC_MSG_DESCRIPTOR
    gmd[MSG_KEY__TYPE] = {
        "name": MSG_KEY__TYPE,
        "mandatory": True
    }
    gmd[MSG_KEY__VERSION] = {
        "name": MSG_KEY__VERSION,
        "mandatory": True, 
        "default": 0
    }
    gmd[MSG_KEY__UUID] = {
        "name": MSG_KEY__UUID,
        "mandatory": True, 
        "default": str(uuid.uuid4())
    }
    # print( gmd[MSG_KEY__UUID]["default"])
_configure_generic_msg_descriptor()

MATCHMAP_KEY__INDEX= "index"
MATCHMAP_KEY__DESCRIPTION= "desc"
MATCHMAP_KEY__IP_PROTOCOL_NUMBER= "ip_prot_num"
MATCHMAP_KEY__DESTINATION_IP= "dst_ip"
MATCHMAP_KEY__DESTINATION_PORT= "dst_port"
MATCHMAP_KEY__NETMASK= "netmask"
MATCHMAP_KEY__NEW_DESTINATION_IP= "new_dst_ip"
MATCHMAP_KEY__NEW_DESTINATION_PORT= "new_dst_port"
MATCHMAP_KEY__UUID= "uuid"
MATCHMAP_DESCRIPTOR = {}
def _configure_matchmap_descriptor():
    md = MATCHMAP_DESCRIPTOR
    md[MATCHMAP_KEY__INDEX] = {
        "name": "index",
        "mandatory": True, 
        "default": 0
    }
    md[MATCHMAP_KEY__DESCRIPTION] = {
        "name": "description",
        "mandatory": True,
        "default": None
    }
    md[MATCHMAP_KEY__IP_PROTOCOL_NUMBER] = {
        "name": "ip_protocol_number",
        "mandatory": True,
        "default": 1
    }
    md[MATCHMAP_KEY__DESTINATION_IP] = {
        "name": "destination_ip",
        "mandatory": False,
        "deafult": None
    }
    md[MATCHMAP_KEY__DESTINATION_PORT] = {
        "name": "destination_port",
        "mandatory": False,
        "default": 0
    }
    md[MATCHMAP_KEY__NETMASK] = {
        "name": "netmask",
        "mandatory": False,
        "default": 32
    }
    md[MATCHMAP_KEY__NEW_DESTINATION_IP] = {
        "name": "new_destination_ip",
        "mandatory": False,
        "deafult": None
    }
    md[MATCHMAP_KEY__NEW_DESTINATION_PORT] = {
        "name": "new_destination_port",
        "mandatory": False,
        "default": 0
    }
    md[MATCHMAP_KEY__UUID] = {
        "name": "uuid",
        "mandatory": True,
        "default": None
    }
_configure_matchmap_descriptor()

UE_KEY__UE_IP = 'ue_ip'
UE_KEY__ENB_IP = 'enb_ip'
UE_KEY__TEID_DOWNLINK = 'teid_downlink'
UE_KEY__EPC_IP = 'epc_ip'
UE_KEY__TEID_UPLINK = 'teid_uplink'
UE_DESCRIPTOR = {}
def _configure_ue_descriptor():
    ud = UE_DESCRIPTOR
    ud[UE_KEY__UE_IP] = {
        "name": UE_KEY__UE_IP,
        "mandatory": True
    }
    ud[UE_KEY__ENB_IP] = {
        "name": UE_KEY__ENB_IP,
        "mandatory": True
    }
    ud[UE_KEY__TEID_DOWNLINK] = {
        "name": UE_KEY__TEID_DOWNLINK,
        "mandatory": True
    }
    ud[UE_KEY__EPC_IP] = {
        "name": UE_KEY__EPC_IP,
        "mandatory": True
    }
    ud[UE_KEY__TEID_UPLINK] = {
        "name": UE_KEY__TEID_UPLINK,
        "mandatory": True
    }
_configure_ue_descriptor()

HELLO_MSG_KEY__TAG = "tag"
HELLO_MSG_KEY__EVERY = "every"
HELLO_MSG_DESCRIPTOR = {}
def _configure_hello_msg_descriptor():
    global HELLO_MSG_DESCRIPTOR
    HELLO_MSG_DESCRIPTOR = copy.deepcopy(GENERIC_MSG_DESCRIPTOR)
    
    hmd = HELLO_MSG_DESCRIPTOR
    hmd[HELLO_MSG_KEY__TAG] = {
        "name": HELLO_MSG_KEY__TAG,
        "mandatory": True, 
        "default": None
    }
    hmd[HELLO_MSG_KEY__EVERY] = {
        "name": HELLO_MSG_KEY__EVERY,
        "mandatory": True, 
        "default": None
    }
_configure_hello_msg_descriptor()

MATCH_ADD_MSG_KEY__MATCH = "match"
MATCH_ADD_MSG_DESCRIPTOR = {}
def _configure_match_add_msg_descriptor():
    global MATCH_ADD_MSG_DESCRIPTOR
    MATCH_ADD_MSG_DESCRIPTOR = copy.deepcopy(GENERIC_MSG_DESCRIPTOR)
    
    mamd = MATCH_ADD_MSG_DESCRIPTOR
    mamd[MATCH_ADD_MSG_KEY__MATCH] = {
        "name": MATCH_ADD_MSG_KEY__MATCH,
        "mandatory": True, 
        "default": {}
    }
_configure_match_add_msg_descriptor()

# MATCH_DELETE_MSG_KEY__MATCH_INDEX = "match_index"
# MATCH_DELETE_MSG_VALUE__DELETE_ALL = -1
# MATCH_DELETE_MSG_DESCRIPTOR = {}
# def _configure_match_action_result_msg_descriptor():
#     global MATCH_DELETE_MSG_DESCRIPTOR
#     MATCH_DELETE_MSG_DESCRIPTOR = copy.deepcopy(GENERIC_MSG_DESCRIPTOR)
    
#     mdmd = MATCH_DELETE_MSG_DESCRIPTOR
#     mdmd[MATCH_DELETE_MSG_KEY__MATCH_INDEX] = {
#         "name": MATCH_DELETE_MSG_KEY__MATCH_INDEX,
#         "mandatory": True, 
#         "default": 0
#     }
# _configure_match_action_result_msg_descriptor()


MATCH_DELETE_MSG_KEY__MATCH_UUID = "match_uuid"
MATCH_DELETE_MSG_VALUE__DELETE_ALL = None
MATCH_DELETE_MSG_DESCRIPTOR = {}
def _configure_match_delete_msg_descriptor():
    global MATCH_DELETE_MSG_DESCRIPTOR
    MATCH_DELETE_MSG_DESCRIPTOR = copy.deepcopy(GENERIC_MSG_DESCRIPTOR)
    
    mdmd = MATCH_DELETE_MSG_DESCRIPTOR
    mdmd[MATCH_DELETE_MSG_KEY__MATCH_UUID] = {
        "name": MATCH_DELETE_MSG_KEY__MATCH_UUID,
        "mandatory": True, 
        "default": MATCH_DELETE_MSG_VALUE__DELETE_ALL
    }
_configure_match_delete_msg_descriptor()

MATCH_ACTION_RESULT_MSG_KEY__MATCH_INDEX = "match_index"
MATCH_ACTION_RESULT_MSG_KEY__STATUS = "status"
MATCH_ACTION_RESULT_MSG_KEY__REASON = "reason"
MATCH_ACTION_RESULT_MSG_DESCRIPTOR ={}
def _configure_match_action_result_msg_descriptor():
    global MATCH_ACTION_RESULT_MSG_DESCRIPTOR
    MATCH_ACTION_RESULT_MSG_DESCRIPTOR = copy.deepcopy(GENERIC_MSG_DESCRIPTOR)
    
    marmd = MATCH_ACTION_RESULT_MSG_DESCRIPTOR
    marmd[MATCH_ACTION_RESULT_MSG_KEY__MATCH_INDEX] = {
        "name": "match_index",
        "mandatory": True, 
        "default": 0
    }
    marmd[MATCH_ACTION_RESULT_MSG_KEY__STATUS] = {
        "name": "status",
        "mandatory": True, 
        "default": 0
    }
    marmd[MATCH_ACTION_RESULT_MSG_KEY__REASON] = {
        "name": "reason",
        "mandatory": True, 
        "default": None
    }
_configure_match_action_result_msg_descriptor()

UE_MAP_MSG_DESCRIPTOR ={}
def _configure_ue_map_msg_descriptor():
    global UE_MAP_MSG_DESCRIPTOR
    UE_MAP_MSG_DESCRIPTOR = copy.deepcopy(GENERIC_MSG_DESCRIPTOR)
_configure_ue_map_msg_descriptor()

class DictionaryWrapper():

    _descriptor= {}
    _dict= {}

    def __init__(self, descriptor, my_dict={}):
        setattr(self, "_descriptor", descriptor)
        for key in self._descriptor.keys():
            self.add_key(key)
        self.set_dict(my_dict)

    def is_valid_key(self, key):
        return key in self._descriptor.keys()

    def is_mandatory_key(self, key):
        if self.is_valid_key(key):
            # print( key )
            # print( self._descriptor[key] ) 
            # print( self._descriptor[key]['mandatory'] ) 
            return self._descriptor[key]['mandatory']
        return False

    def get_default_value(self, key):
        if "default" in self._descriptor[key]:
            return self._descriptor[key]['default']
        return None

    def get_key_name(self, key):
        if self.is_valid_key(key):
            return self._descriptor[key]['name']
        return ""

    def set_value(self, key, value):
        self._dict[key] = value

    def get_value(self, key):
        return self._dict[key]

    def build_default(self):
        for key in self._descriptor.keys():
            # if (self.is_mandatory_key(key)):
            self.set_value(key, self.get_default_value(key))
        if MSG_KEY__UUID in self._descriptor.keys():
            self.set_value(MSG_KEY__UUID, str(self.generate__uuid()))
        return self

    def reset(self):
        setattr(self, "_dict", {})
        self.build_default()

    def set_dict(self, new_dict):
        self.reset()
        self.update_data(new_dict)

    def get_dict(self):
        return copy.deepcopy(self._dict)

    def get_msg(self):
        return json.dumps(self._dict)

    def update_data(self, original):
        for key in original:
            self.set_value(key, original[key])

    def generate__get_key(self, key):
        return "_get__" + self.get_key_name(key)
    
    def generate__set_key(self, key):
        return "_set__"+ self.get_key_name(key)

    def generate__get_key_default(self, key):
        return "_get__" + self.get_key_name(key) + "_default"

    def generate__uuid(self):
        return uuid.uuid4()

    def add_key(self, key):
        
        def _set(value):
            return self.set_value(key, value)

        def _get():
            return self.get_value(key)

        def _default():
            return self.get_default_value(key)

        setattr(self, self.generate__get_key(key), _get)
        setattr(self, self.generate__get_key_default(key), _default)
        setattr(self, self.generate__set_key(key), _set)

    def validate(self):
        for key in self._descriptor.keys():
            if (self.is_mandatory_key(key)):
                # if self._dict.get(key) == None:
                if key not in self._dict:
                    print("Missing mandatory key %s", key)
                    return False
        return True

class MatchmapDictionaryWrapper(DictionaryWrapper):
    
    def __init__(self, my_dict={}):
        DictionaryWrapper.__init__(self, MATCHMAP_DESCRIPTOR, my_dict)

class UEDictionaryWrapper(DictionaryWrapper):
    
    def __init__(self, my_dict={}):
        DictionaryWrapper.__init__(self, UE_DESCRIPTOR, my_dict)

class GenericMsgDictionaryWrapper(DictionaryWrapper):
    def __init__(self, my_dict={}):
        DictionaryWrapper.__init__(self, GENERIC_MSG_DESCRIPTOR, my_dict)

class HelloMsgDictionaryWrapper(DictionaryWrapper):
    def __init__(self, my_dict={}):
        DictionaryWrapper.__init__(self, HELLO_MSG_DESCRIPTOR, my_dict)
        self._set__type(MSG_TYPE__HELLO)

class MatchAddMsgDictionaryWrapper(DictionaryWrapper):
    
    def __init__(self, my_dict={}):
        DictionaryWrapper.__init__(self, MATCH_ADD_MSG_DESCRIPTOR, my_dict)
        self._set__type(MSG_TYPE__MATCH_ADD)

class MatchDeleteMsgDictionaryWrapper(DictionaryWrapper):
    
    def __init__(self, my_dict={}):
        DictionaryWrapper.__init__(self, MATCH_DELETE_MSG_DESCRIPTOR, my_dict)
        self._set__type(MSG_TYPE__MATCH_DELETE)

    def set__delete_all(self):
        self._set__match_uuid(MATCH_DELETE_MSG_VALUE__DELETE_ALL)
        return self

class MatchActionResultMsgDictionaryWrapper(DictionaryWrapper):
    
    def __init__(self, my_dict={}):
        DictionaryWrapper.__init__(self, 
                                    MATCH_ACTION_RESULT_MSG_DESCRIPTOR, my_dict)
        self._set__type(MSG_TYPE__MATCH_ACTION_RESULT)

class UEMapMsgDictionaryWrapper(DictionaryWrapper):

    def __init__(self, my_dict={}):
        DictionaryWrapper.__init__(self, UE_MAP_MSG_DESCRIPTOR, my_dict)
        # self._set__type(MSG_TYPE__UE_MAP)

    def get__ue_map(self):
        ue_map = {}
        for key in self.get_dict().keys():
            if (key != MSG_KEY__TYPE) & (key != MSG_KEY__VERSION) &\
                (key != MSG_KEY__UUID):
                ue_map[key] = self.get_value(key)
        return ue_map

class DictionaryWrapperFactory():

    def __init(self):
        pass

    @staticmethod
    def detect_msg(my_dict):
        msg = GenericMsgDictionaryWrapper(my_dict)
        mtype = msg._get__type()

        if mtype == MSG_TYPE__MATCH_ADD:
            return MatchAddMsgDictionaryWrapper(my_dict)
        if mtype == MSG_TYPE__MATCH_DELETE:
            return MatchDeleteMsgDictionaryWrapper(my_dict)
        if mtype == MSG_TYPE__HELLO:
            return HelloMsgDictionaryWrapper(my_dict)
        if mtype == MSG_TYPE__MATCH_ACTION_RESULT:
            return MatchActionResultMsgDictionaryWrapper(my_dict)
        if mtype == MSG_TYPE__UE_MAP:
            return UEMapMsgDictionaryWrapper(my_dict)
        
        return GenericMsgDictionaryWrapper(my_dict)

