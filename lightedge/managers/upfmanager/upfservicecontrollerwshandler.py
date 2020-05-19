import uuid
import copy
import time
import json
import uuid
import traceback
import tornado.web
# import tornado.ioloop
import tornado.websocket
import logging
import threading
from tornado.ioloop import IOLoop
from logging import Logger
from queue import Queue, Empty
from threading import Timer
import asyncio
import random

from pprint import pformat

from lightedge.managers.upfmanager.match import Match

from lightedge.managers.upfmanager.dictionarywrapper import *

MATCH_OP__ADD = 'add'
MATCH_OP__DELETE = 'delete'
class MatchOp():

    def __init__(self, data, op=MATCH_OP__ADD):
        self.data = data
        self.op = op
        

STATUS__NOT_INITIALIZED = "NOT_INITIALIZED"    
STATUS__INITIALIZING = "INITIALIZING"
STATUS__INITIALIZED = "INITIALIZED"

UPF_CLIENT_HANDLER_LOG_TAG = "UPF_CH__"

STATUS_LIST = [ STATUS__NOT_INITIALIZED, 
                STATUS__INITIALIZING, 
                STATUS__INITIALIZED]

QUEUE_CHECK_TIME_INTERVAL = 5.0
class UPFServiceControllerWSHandler(tornado.websocket.WebSocketHandler):

    MSG_HANDLER__INVALID = None
    HELLO_MSG__DEFAULT_EVERY = 30
    HELLO_MSG__MAX_EVERY_MISSED = 5


    def __init__(self, *args, **kwargs):
        super(UPFServiceControllerWSHandler, self).__init__(*args) #, **kwargs)

        self.name = "PreInitialization"

        self.set_log()
        # self.log.debug(kwargs)
        for key, value in kwargs.items():
            if key == "trigger_upf_client_init":
                self._init_function = value
            if key == "leave_manager":
                self._leave_function = value
            # self.log.debug("{0} = {1}".format(key, value))

        self.counter = 0
        
        self._matchop_queue = Queue()

        self._queue_check_timer = None

        self._status = STATUS__NOT_INITIALIZED

        self._hello_tag = None
        self._hello_every = None
        self.set_params__hello_every()
        self._last_hello_time = None
        self.set_params__last_hello_time()
        self._ongoing_matchop = None

        self._local_matches = []

        self.log.debug("UPFServiceWSHandler %s initialized", __name__)

        # asyncio.set_event_loop(asyncio.new_event_loop())

        # IOLoop.instance().start()

    def add_local_match(self, index, match):
        self._local_matches.insert(index, match)
        self.update_local_matches_index()

    def delete_local_match(self, match_uuid):
        if match_uuid is None:
            self._local_matches.clear()
            return None
        for index in range(len(self._local_matches)):
            if match_uuid == self._local_matches[index].to_dict()["uuid"]:
                self._local_matches.pop(index)
                self.update_local_matches_index()
                return index
        return -1

    def update_local_matches_index(self):
        new_list = []
        for i in range(len(self._local_matches)):
            data = self._local_matches[i].to_dict()
            self._local_matches[i].from_dict(i, data)
            new_list.insert(i, self._local_matches[i])
        self._local_matches = new_list


    def trigger_init(self):
        self.name = self.get_params__id()
        self.set_log()
        self.set_params__status__INITIALIZING()
        self._init_function(self)
        self.queue_check()
        self.set_params__status__INITIALIZED()

    def leave_manager(self):
        return self._leave_function(self)

    def start_queue_check_timer(self):

        if self._queue_check_timer is not None:
            self._queue_check_timer.cancel()
        self._queue_check_timer = Timer(QUEUE_CHECK_TIME_INTERVAL, 
                                        self.queue_check)
        self._queue_check_timer.start() 
        # self.log.debug("queue check timer started")

    def cancel_queue_check_timer(self):

        if self._queue_check_timer is None:
            return
        self._queue_check_timer.cancel()
        # self.log.debug("queue check timer cancelled")

    def queue_check(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        # self.log.info("\n\n       QUEUE CHECK!")
        # tname = threading.current_thread().name
        # self.log.debug("THREAD NAME: %s", tname)
        # self.log.debug("THREAD LIST: %s", threading.enumerate())
        if not self.check_params__last_hello_time():
            self.log.error("MAXIMUM DELAY from last HELLO MSG reached: closing")
            self.close()
            return
        # else:
        #     self.log.info("LAST HELLO TIME OK: %i" % self.get_params__last_hello_time())
        self.cancel_queue_check_timer()  
        if self.is_matchop_ongoing():
            self.log.debug(
                "ONGOING MATCH_OP (%s), queue_check postponed",
                self.get_params__ongoing_matchop())
            self.start_queue_check_timer()
            return
        try:
            match_op = self.pop_matchop(block=False)
            if match_op is not None:
                self.process_match_op(match_op)
            self.queue_check()
        except Empty:
            # self.log.info("Empty queue")
            self.start_queue_check_timer()
        except Exception:
            tb = traceback.format_exc()
            ident = threading.current_thread().name
            self.log.error("\n\n\nERROR!!!!!\n%s\n%s",tb, ident)
            self.cancel_queue_check_timer() 
            self.start_queue_check_timer() 

    def push_matchop(self, op):
        # self.log.info("Before PUSH qsize: %i", self._matchop_queue.qsize())
        self._matchop_queue.put(op)
        self.log.debug("After PUSH qsize: %i", self._matchop_queue.qsize())

    def pop_matchop(self, block=True):
        # self.log.info("Before POP qsize: %i", self._matchop_queue.qsize())
        op = self._matchop_queue.get(block=block)
        self.log.debug("After POP qsize: %i", self._matchop_queue.qsize())
        self.log.debug("Popped Op: %s", op)
        return op

    def process_match_op(self, match_op):
        # time.sleep(0.2)
        self.log.debug("processing match_op: %s", match_op)
        self.set_params__ongoing_matchop(-1)
        if match_op['type'] == MSG_TYPE__MATCH_DELETE:
            delete_msg = MatchDeleteMsgDictionaryWrapper()
            # self.log.debug("\n\n DEFAULT DELETE MSG:\n%s", delete_msg.get_dict())
            delete_msg = delete_msg.get_dict()
            for key in match_op.keys():
                delete_msg[key] = match_op[key]            # self.send_message(delete_msg)
            # self.log.info("\n\n DELETE MSG to be sent:\n%s", delete_msg)
            self.set_params__ongoing_matchop(delete_msg)
            self.send_message(delete_msg)

        elif match_op['type'] == MSG_TYPE__MATCH_ADD:
            add_msg = MatchAddMsgDictionaryWrapper()
            # self.log.debug("\n\n DEFAULT ADD MSG:\n%s", add_msg.get_dict())
            del match_op ["type"]
            add_msg._set__match(match_op)
            add_msg._set__uuid(match_op["uuid"])
            add_msg = add_msg.get_dict()
            # self.log.info("\n\n ADD MSG to be sent:\n%s", add_msg)
            self.set_params__ongoing_matchop(add_msg)
            self.send_message(add_msg)

        else:
            self.set_params__ongoing_matchop()
            pass


    def get_descriptor(self):
        descriptor = {}
        descriptor["id"] = self.get_params__id()
        descriptor["tag"] = self.get_params__hello_tag()
        descriptor["remote_address"] = self.get_params__remote_address()
        descriptor["remote_port"] = self.get_params__remote_port()
        descriptor["uemap"] = self.get_params__ue_map()
        descriptor["local_matches"] = []
        descriptor["stringified"] = ""
        # self.log.info(self._local_matches)
        for i in range(len(self._local_matches)):
            descriptor["local_matches"].insert(
                i,
                # self._local_matches[i].to_str_with_desc())
                self._local_matches[i].to_dict())
            descriptor["stringified"] = descriptor["stringified"] +\
                                        self._local_matches[i].to_str_with_desc()
        return descriptor

    def get_params__id(self):
        return "{0}@{1}:{2}".format(self.get_params__hello_tag(),
                                    self.get_params__remote_address(),
                                    self.get_params__remote_port())

    def get_params__remote_address(self):
        return self.request.connection.context.address[0]

    def get_params__remote_port(self):
        return self.request.connection.context.address[1]

    def get_params__matchop_queue(self):
        return self._matchop_queue

    def set_params__status(self, status):
        if status in STATUS_LIST:
            old_status = self.get_params__status()
            self._status = status
            self.log.info("Status change: from %s to %s", old_status, status)
    
    def set_params__status__NOT_INITIALIZED(self):
        return self.set_params__status(STATUS__NOT_INITIALIZED)

    def set_params__status__INITIALIZING(self):
        return self.set_params__status(STATUS__INITIALIZING)

    def set_params__status__INITIALIZED(self):
        return self.set_params__status(STATUS__INITIALIZED)

    def is_status__NOT_INITIALIZED(self):
        return self.get_params__status() == STATUS__NOT_INITIALIZED

    def is_status__INITIALIZING(self):
        return self.get_params__status() == STATUS__INITIALIZING

    def is_status__INITIALIZED(self):
        return self.get_params__status() == STATUS__INITIALIZED
    
    def get_params__status(self):
        return self._status

    def get_params__hello_tag(self):
        return self._hello_tag

    def get_params__hello_every(self):
        return self._hello_every

    def get_params__last_hello_time(self):
        return self._last_hello_time

    def set_params__hello_tag(self, hello_tag):
        # if hello_tag is None:
        #     hello_tag = ""
        self._hello_tag = hello_tag

    def set_params__hello_every(self, every=None):
        if (every is None) or (every <=0):
            self._hello_every = self.HELLO_MSG__DEFAULT_EVERY
        else:
            self._hello_every = every

    def set_params__last_hello_time(self, timestamp=None):
        if (timestamp is None) or (timestamp <=0):
            self._last_hello_time = time.time()
        else:
            self._last_hello_time = timestamp

    def check_params__hello_tag(self, tag):
        if ((tag is None) and (self.get_params__hello_tag() is None) or\
            (tag == self.get_params__hello_tag())):
            return True
        return False

    def check_params__last_hello_time(self):
        delta  = time.time() - self.get_params__last_hello_time() 
        max_delay = self.get_params__hello_every() * self.HELLO_MSG__MAX_EVERY_MISSED
        if delta > max_delay:
            return False
        return True

    def set_params__ue_map(self, ue_map):
        self._ue_map = ue_map

    def get_params__ue_map(self):
        return self._ue_map

    def set_params__ongoing_matchop(self, matchop=None):
        self.log.debug("ONGOING MATCHOP set to: %s", matchop)
        self._ongoing_matchop = matchop
    
    def get_params__ongoing_matchop(self):
        return self._ongoing_matchop

    def is_matchop_ongoing(self):
        return self.get_params__ongoing_matchop() is not None

    def check_ongoing_matchop_uuid(self, uuid):
        if self.is_matchop_ongoing():
            matchop = self.get_params__ongoing_matchop()
            if matchop["uuid"] == uuid:
                return True
            else:
                return False
        self.log.warning("check_matchop_uuid whit NO ONGOING MATCHOP")
        return True
    
    def set_log(self):
        
        # if name is not None:
        #     self.log = logging.getLogger(name)
        #     return
        self.log = logging.getLogger(UPF_CLIENT_HANDLER_LOG_TAG + self.name)
        logging.getLogger("asyncio").setLevel(logging.WARNING)
        self.log.setLevel(logging.INFO)
    
    def open(self):
        # if not hasattr(self, 'LOG'):
        #     self.set_log()
        self.log.info("Open connection with %s , port %s",
                      #  self.request.remote_ip,
                      self.request.connection.context.address[0],
                      self.request.connection.context.address[1])
                      #  self.stream.socket.getpeername()[1])
        
        # self.trigger_init()

    def on_message(self, message):
        # self.log.debug("UPF Client Handler id: %s", self.get_params__id())
        self.log.debug("New message: \n%s", message)
        # self.counter = self.counter + 1
        # if self.counter > 5:
        #     self.close()
        try:
            msg = DictionaryWrapperFactory.detect_msg(json.loads(message))
            # self.log.debug("New message formatted: \n%s", 
            #                pformat(msg.get_dict()))
            # self.log.debug( msg )
            if msg.validate():
                # self.log.debug( "VALID Message" )
                pass
            else:
                self.log.debug( "INVALID Message" )
            self.handle_message(msg)
        except ValueError as e:
            self.log.error("Invalid input: %s\n%s", message, e)
        except AssertionError:
            self.log.error("Invalid msg: %s", msg)

    def on_close(self):
        self.log.info("Closing connection")
        self.leave_manager()
        pass

    def get_handler_by_msg_type(self, msg_type):
        """Return msg handler associated to a given msg_type"""

        # self.log.debug("get_handler_by_msg_type: %s", msg_type)

        handler = self.MSG_HANDLER__INVALID

        handler_name = "_handle__%s" % msg_type

        # self.log.debug("handler_name: %s", handler_name)

        try:

            assert hasattr(self, handler_name)
            handler = getattr(self, handler_name)

        except AssertionError:

            self.log.error("UNKNOWN handler method %s", handler_name)

        finally:
            # self.log.debug("handler: %s", handler)
            return handler

    def is_valid_handler(self, handler):
        return handler != self.MSG_HANDLER__INVALID

    def _handle__default(self, msg):
        self.log.warning("Default Handler")
        return self._handle__do_nothing(msg)

    def _handle__do_nothing(self, msg):
        self.log.warning("Doing nothing with msg: %s", msg)

    def handle_message(self, msg):

        try:

            msg_type = msg._get__type()

            if self.is_status__INITIALIZED():
                pass
            elif self.is_status__INITIALIZING():
                if msg_type == MSG_TYPE__HELLO:
                    pass
                else:
                    self.discard_msg(msg)
                    return
            elif self.is_status__NOT_INITIALIZED():
                if msg_type == MSG_TYPE__HELLO:
                    pass
                else:
                    self.discard_msg(msg)
                    return

            # if not self.check__first_hello_arrived():
            #     if msg_type == MSG_TYPE__HELLO:
            #         self.handle__hello(msg)
            #         return
            #     else:
            #         self.discard_msg(msg)
            #         return

            # if self.check__waiting_delete_all_result():
            #     if msg_type != MSG_TYPE__MATCH_ACTION_RESULT:
            #         self.discard_msg(msg)
            #         return

            msg_handler = self.get_handler_by_msg_type(msg_type)
            if not self.is_valid_handler(msg_handler):
                raise ValueError("Invalid Handler")
            
            msg_handler(msg)

        except ValueError as e:
            self.log.error(e) 

    def _handle__hello(self, msg):
        self.log.debug("Handling: HELLO msg")

        self.set_params__hello_every(msg._get__every())
        self.set_params__last_hello_time()

        if self.is_status__NOT_INITIALIZED():
            self.handle__first_hello(msg)
        else:
            msg_tag = msg._get__tag()
            if self.check_params__hello_tag(msg_tag):
                # self.log.debug("CONSISTENT HELLO TAG")
                pass
            else:
                self.log.warning("HELLO TAG INCONSISTENCY")
        self.log.debug("\n")

    # def _handle__match_add(self, msg):
    #     self.log.info("MATCH_ADD msg")

    # def _handle__match_delete(self, msg):
    #     self.log.info("MATCH_DELETE msg")

    def _handle__match_action_result(self, msg):
        self.log.info("Handling: MATCH_ACTION_RESULT msg")

        msg_uuid = msg._get__uuid()
        if not self.check_ongoing_matchop_uuid(msg_uuid):
            self.log.warning("RESPONSE UUID NOT MATCHING WITH REQUEST UUID")
            self.discard_msg(msg)
        else:
            ongoing_matchop_type = self.get_params__ongoing_matchop()["type"]
            response = msg._get__status()
            if ongoing_matchop_type == MSG_TYPE__MATCH_DELETE:
                if response == 204:
                    # self.log.info(
                    #     "\nPOSITIVE RESPONSE (%s) to ongoing MATCHOP: %s",
                    #     response,
                    #     self.get_params__ongoing_matchop())
                    match_uuid = self.get_params__ongoing_matchop()["match_uuid"]

                    index = self.delete_local_match(match_uuid)

                    if match_uuid == None:
                        match = "ALL matches"
                    else:
                        if index == -1:
                            match = "NON EXISTENT RULE with uuid %s" % (match_uuid)
                        else:
                            match = "match[%i] with uuid %s" % (index, match_uuid)
                    self.log.info(
                        "SUCCESSFUL DELETION (%i) of %s",
                        response,
                        match)

                    self.set_params__ongoing_matchop()
                    self.queue_check()
                else:
                    reason = msg._get__reason()
                    # self.log.info(
                    #     "\nNEGATIVE RESPONSE (%s) to ongoing MATCHOP: %s\nReason: %s",
                    #     response,
                    #     self.get_params__ongoing_matchop(),
                    #     reason)
                    match_uuid = self.get_params__ongoing_matchop()["match_uuid"]
                    
                    index = self.delete_local_match(match_uuid)

                    if match_uuid == None:
                        match = "ALL matches"
                    else:
                        if index == -1:
                            match = "NON EXISTENT RULE with uuid %s" % (match_uuid)
                        else:
                            match = "match[%i] with uuid %s" % (index, match_uuid)
                    self.log.warning(
                        "FAILED DELETION (%i) of %s with reason: %s",
                        response,
                        match,
                        reason)
                    # self.log.warning(
                    #     "FAILED DELETION (%i) of rule %i with reason: %s",
                    #     response,
                    #     self.get_params__ongoing_matchop()["match_index"],
                    #     reason)
                    self.set_params__ongoing_matchop()
                    self.queue_check()
                    # self.close()
            if ongoing_matchop_type == MSG_TYPE__MATCH_ADD:
                if response == 201:
                    # self.log.info(
                    #     "\nPOSITIVE RESPONSE (%s) to ongoing MATCHOP: %s",
                    #     response,
                    #     self.get_params__ongoing_matchop())
                    match_data = self.get_params__ongoing_matchop()["match"]
                    match_index = match_data["index"]
                    match = Match()
                    match.from_dict(
                        match_index, 
                        match_data)

                    self.add_local_match(match_index, match)

                    self.log.info(
                        "SUCCESSFUL ADD (%i) at #%i of match: %s",
                        response,
                        match_index,
                        match.to_str_with_desc())
                    self.set_params__ongoing_matchop()
                    self.queue_check()
                else:
                    reason = msg._get__reason()
                    # self.log.info(
                    #     "\nNEGATIVE RESPONSE (%s) to ongoing MATCHOP: %s\nReason: %s",
                    #     response,
                    #     self.get_params__ongoing_matchop(),
                    #     reason)
                    match_data = self.get_params__ongoing_matchop()["match"]
                    match_index = match_data["index"]
                    match = Match()
                    match.from_dict(
                        match_index, 
                        match_data)
                    self.log.warning(
                        "FAILED ADD (%i) at %i of match %s with reason: %s",
                        response,
                        match_index,
                        match.to_str_with_desc(),
                        reason)
                    self.set_params__ongoing_matchop()
                    self.queue_check()
                    # self.close()
        


    def _handle__ue_map(self, msg):
        self.log.debug("Handling: UE_MAP msg")
        previous_ue_map = self.get_params__ue_map()
        updated_ue_map = msg.get__ue_map()
        if random.randint(1,3) == -1:
            updated_ue_map = self.test_generate_fake_uemap()
            self.set_params__ue_map(updated_ue_map)
            if json.dumps(previous_ue_map) != json.dumps(updated_ue_map):
                self.log.info("ue_map UPDATED: %s", updated_ue_map)

    def discard_msg(self, msg):
        self.log.warning("DISCARDING MSG: %s", msg.get_msg() )

    # def handle__client_connectivity_loss(self):
    #     self.set_flag__first_hello_arrived(False)

    def handle__first_hello(self, msg):

        self.log.info("Handling: first HELLO msg")

        msg_tag = msg._get__tag()
        self.set_params__hello_tag(msg_tag)
        self.log.debug("UPDATED UPF Client Handler id: %s", self.get_params__id())
        self.trigger_init()

    # def handle__add_new_rule(self, msg):
    #     self.log.info("Handling a new Rule request")
    #     pass


    def send_message(self, message={}, mcls=None):

        self.write_message(json.dumps(message, cls=mcls))
        self.log.debug("MESSAGE SENT: \n%s", message)

    # def send_message__delete_all(self):

    #     delete_msg = MatchDeleteMsgDictionaryWrapper().set__delete_all()

    #     self.set_flag__last_delete_all_msg_uuid(delete_msg._get__uuid())

    #     self.send_message(delete_msg.get_dict())

    #     self.set_flag__waiting_delete_all_result(True)


    def test_generate_fake_uemap(self):
        fake_uemap = {}
        entries = random.randint(1,4)
        for x in range(entries):
            ue_ip = "10.%i.0.%i" % (random.randint(1,255),
                                    random.randint(1,255))
            enb_ip = "10.0.%i.%i" % (random.randint(1,255),
                                    random.randint(1,255))
            teid_uplink = "0x"+"{:08d}".format(random.randint(1,99999999))
            epc_ip = "10.%i.%i.%i" % (random.randint(1,255),
                                    random.randint(1,255),
                                    random.randint(1,255))
            teid_downlink = "0x"+"{:08d}".format(random.randint(1,99999999))
            fake_uemap[ue_ip]= {
                "ue_ip": ue_ip,
                "enb_ip": enb_ip,
                "teid_uplink": teid_uplink,
                "epc_ip": epc_ip,
                "teid_downlink": teid_downlink
            }

        return fake_uemap