$('#upfmanager').removeClass('collapsed');
$('#collapse_upfmanager').addClass('show');
$('#matchmap').addClass('active');

console.log("__LIGHTEDGE_WEBUI",__LIGHTEDGE_WEBUI)

$(document).ready(function() {

  CF = __LIGHTEDGE_WEBUI.CORE_FUNCTIONS

  ENTITY = __LIGHTEDGE_WEBUI.ENTITY.MATCHMAP

  // MODAL_FIELD__ADDRESS= "address"
  // MODAL_FIELD__DESCRIPTION= "desc"

  DEFAULT_PRIORITY_VALUE = 1
  DEFAULT_DESCRIPTION_VALUE = ""
  DEFAULT_IP_PROTOCOL_SELECT_VALUE = 6 // TCP protocol
  DEFAULT_IP_PROTOCOL_NUMBER_VALUE = 6
  DEFAULT_IP_PROTOCOL_NUMBER_CUSTOM_VALUE = 0
  DEFAULT_DESTINATION_IP_VALUE = ""
  DEFAULT_DESTINATION_PORT_VALUE = 0
  DEFAULT_NETMASK_VALUE = 32
  DEFAULT_NEW_DESTINATION_IP_VALUE = ""
  DEFAULT_NEW_DESTINATION_PORT_VALUE = 0

  IP_PROTOCOL_SELECT_OPTIONS = [
    {
      label: "ICMP",
      value: 1,
      allow_port: false
    },
    {
      label: "TCP",
      value: 6,
      allow_port: true
    },
    {
      label: "UDP",
      value: 17,
      allow_port: true
    },
    {
      label: "SCTP",
      value: 132,
      allow_port: true
    },
    {
      label: "CUSTOM",
      value: "",
      allow_port: false
    }
  ]

  FIELDS = {
    priority: {
      type: "TEXT",
      default: DEFAULT_PRIORITY_VALUE,
    },
    desc: {
      type: "TEXT",
      default: DEFAULT_DESCRIPTION_VALUE
    },
    ip_proto_select: {
      type: "SELECT",
      default: DEFAULT_IP_PROTOCOL_SELECT_VALUE,
    },
    ip_proto_num: {
      type: "TEXT",
      default: DEFAULT_IP_PROTOCOL_NUMBER_VALUE
    },
    dst_ip: {
      type: "TEXT",
      default: DEFAULT_DESTINATION_IP_VALUE
    },
    dst_port: {
      type: "TEXT",
      default: DEFAULT_DESTINATION_PORT_VALUE
    },
    netmask: {
      type: "TEXT",
      default: DEFAULT_NETMASK_VALUE
    },
    new_dst_ip: {
      type: "TEXT",
      default: DEFAULT_NEW_DESTINATION_IP_VALUE
    },
    new_dst_port: {
      type: "TEXT",
      default: DEFAULT_NEW_DESTINATION_PORT_VALUE
    },
  }

  RESET_DEFAULTS={
    priority: {
      value: DEFAULT_PRIORITY_VALUE,
    },
    desc: {
      value: DEFAULT_DESCRIPTION_VALUE
    },
    ip_proto_select: {
      options: set_options_labels(), //IP_PROTOCOL_SELECT_OPTIONS,
      value: DEFAULT_IP_PROTOCOL_SELECT_VALUE
    },
    ip_proto_num: {
      value: DEFAULT_IP_PROTOCOL_NUMBER_VALUE
    },
    dst_ip: {
      value: DEFAULT_DESTINATION_IP_VALUE
    },
    dst_port: {
      value: DEFAULT_DESTINATION_PORT_VALUE
    },
    netmask: {
      value: DEFAULT_NETMASK_VALUE
    },
    new_dst_ip: {
      value: DEFAULT_NEW_DESTINATION_IP_VALUE
    },
    new_dst_port: {
      value: DEFAULT_NEW_DESTINATION_PORT_VALUE
    },
  }

  ADD_MODAL = new WEBUI_Modal_Entity(
    __LIGHTEDGE_WEBUI.MODAL.TYPE.ADD,
    ENTITY
  ).add_fields(FIELDS)

  reset2modal_defaults(__LIGHTEDGE_WEBUI.MODAL.TYPE.ADD)
  update_selected_pn(__LIGHTEDGE_WEBUI.MODAL.TYPE.ADD)
  update_description()

  REMOVE_MODAL = new WEBUI_Modal_Entity(
    __LIGHTEDGE_WEBUI.MODAL.TYPE.REMOVE,
    ENTITY
  ).add_fields(FIELDS)

  reset2modal_defaults(__LIGHTEDGE_WEBUI.MODAL.TYPE.REMOVE)

  aoColumns = [
    { "sTitle": "Priority" },
    { "sTitle": "Description" },
    { "sTitle": "IP Protocol#" },
    { "sTitle": "DST IP" },
    { "sTitle": "DST Port" },
    { "sTitle": "Netmask" },
    { "sTitle": "NEW DST IP" },
    { "sTitle": "NEW DST Port" },
    { "sTitle": "Actions", "sClass": "text-center" }
  ]

  DATATABLE = $('#dataTable').DataTable({
  "aoColumns": aoColumns
  });  

  refresh_datatable();
});

ENTITY = null
FIELDS = {}
CF = null

function set_options_labels(){
  let options = []
  IP_PROTOCOL_SELECT_OPTIONS.forEach(function(elem, index){
    let obj = {}
    $.each(elem, function(key, item){
      if (key === "label"){
        if (item !== "CUSTOM"){
          obj.label = elem.label + " [" + elem.value + "]"
        }
        else{
          obj.label = item
        }
      }
      else{
        obj[key] = item
      }
    })
    console.log("set_options_labels, ", elem.label,":",obj.label)
    options.push(obj)
  })
  console.log("options:",options)
  return options
}

function reset_modal_ip_proto_select_options(modal_type){
  let modal = null
  switch(modal_type){
    case __LIGHTEDGE_WEBUI.MODAL.TYPE.ADD:
      modal = ADD_MODAL
      break
    case __LIGHTEDGE_WEBUI.MODAL.TYPE.REMOVE:
      modal = REMOVE_MODAL
      break
  }
  if (CF._is_there(modal)){
    let options = []
    IP_PROTOCOL_SELECT_OPTIONS.forEach(function(option){
      let label = option.label + " ["+option.value+"]"
      if (option.label === "CUSTOM"){
        label = option.label
      }
      options.push({
        label: label,
        value: option.value
      })
    })
    modal.ip_proto_select.reset(options)
  }
}

function reset2modal_defaults(modal_type){
  modal = null
  switch(modal_type){
    case __LIGHTEDGE_WEBUI.MODAL.TYPE.ADD:
      modal = ADD_MODAL
      break
    case __LIGHTEDGE_WEBUI.MODAL.TYPE.REMOVE:
      modal = REMOVE_MODAL
      break
  }
  if (CF._is_there(modal)){
    console.log("resetting defaults",modal_type)
    modal.reset(RESET_DEFAULTS)
  }
}

function add() {

  let data = {
    "version":"1.0",
  }

  let index = null
  $.each(FIELDS, function(key, val){
    if (key !== 'priority'){
      if (key === "ip_proto_select"){
        // skip this params
      }
      else if ((key === "dst_port") || (key === "new_dst_port") || (key === "ip_proto_num") || (key === "netmask")){
        data[key] = parseInt(ADD_MODAL[key].get())
        if (Number.isNaN(data[key])){
          switch(key){
            case "new_dst_port":
              data[key] = DEFAULT_NEW_DESTINATION_PORT_VALUE
              break
            case "dst_port":
              data[key] = DEFAULT_DESTINATION_PORT_VALUE
              break
            case "ip_proto_num":
              data[key] = DEFAULT_IP_PROTOCOL_NUMBER_CUSTOM_VALUE
              break
            case "netmask":
              data[key] = DEFAULT_NETMASK_VALUE
              break
          }
        }
        console.log(key, data[key])
      }
      else{
        data[key] = ADD_MODAL[key].get()
      }
    }
    else{

      let value = ADD_MODAL[key].get()
      if (CF._is_there(value) && (value !== "")){
        index = value
      }
      else{
        index = DEFAULT_PRIORITY_VALUE
      }
    }
  })

  if (CF._is_there(index)){
    console.log("priority: ", parseInt(index, 10))  
  }
  else{
    console.log("adding new matchmap with the highest priority") 
  }

  console.log("data: ",data)
  
  let add_reset = function(){
    ADD_MODAL.reset(RESET_DEFAULTS) //.bind(ADD_MODAL)
    update_description()
    update_selected_pn(__LIGHTEDGE_WEBUI.MODAL.TYPE.ADD)
  }

  REST_REQ(ENTITY).configure_POST({
    data: data,
    key: index,
    success: [ lightedge_log_response, lightedge_alert_generate_success, 
      add_reset, refresh_datatable ],
    error: [ lightedge_log_response, lightedge_alert_generate_error ]
  })
  .perform()

}

function trigger_remove_modal( matchmap_key ) {

  show_remove_modal = function(data){

    let index = null
    $.each(FIELDS, function(key, val){
      if (key !== 'priority'){
        REMOVE_MODAL[key].set(data[key])
      }
      else{
        REMOVE_MODAL[key].set(matchmap_key)
      }
    })

    // REMOVE_MODAL.address.set(data.addr)
    // REMOVE_MODAL.desc.set(data.desc)

    REMOVE_MODAL.get_$instance().modal({show:true})
  }

  REST_REQ(ENTITY).configure_GET({
    key: matchmap_key,
    success: [ lightedge_log_response, show_remove_modal],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()
  
}

function remove(){

  let key = REMOVE_MODAL.priority.get()

  console.log("matchmap TO BE REMOVED, key: ", key)
  
  // REMOVE_MODAL.reset(RESET_DEFAULTS)
  reset2modal_defaults(__LIGHTEDGE_WEBUI.MODAL.TYPE.REMOVE)

  REST_REQ(ENTITY).configure_DELETE({
    key: key,
    success: [
      lightedge_log_response, lightedge_alert_generate_success, refresh_datatable ],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()
}

function confirm_remove_all(){
  $("#confirm_REMOVE_ALL_Modal").modal({show:true})
}

function remove_all(){
  REST_REQ(ENTITY).configure_DELETE({
    success: [
      lightedge_log_response, lightedge_alert_generate_success, refresh_datatable ],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()
}


function format_datatable_data( data ) {

  $.each( data["matches"], function( key, val ) {

    let index = val['index']+1

    actions = ""+
      '<button class="btn btn-sm btn-danger shadow-sm mb-xl-1 m-1" '+
      'onclick="trigger_remove_modal(\''+ index +'\')">'+
      '<i class="fas fa-trash fa-sm fa-fw text-white-50 mr-xl-1 m-1"></i><span class="d-none d-xl-inline">Remove</span></button>'

    DATATABLE.row.add([
      "<div class='text-center'>"+index+"</div>",
      val['desc'],
      val['ip_proto_num'],
      val['dst_ip'],
      val['dst_port'],
      val['netmask'],
      val['new_dst_ip'],
      val['new_dst_port'],
      actions
    ] )

  });

  DATATABLE.draw(true)

}

function refresh_datatable() {

  console.log("refreshing datatable")

  DATATABLE.clear();
  REST_REQ(ENTITY).configure_GET({
    key: "checked",
    success: [ lightedge_log_response, format_datatable_data, 
               mismatch_alert_generate_warning],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()

  
}

function update_description(){
  
  let description = ADD_MODAL["desc"].get()
  // console.log("update_description, value = '"+description+"'")
  let button = $("#add_button")
  if (CF._is_there(description) &&
     (description !== "")){
    // console.log("enabled")
    CF._enable(button)
  }
  else{
    // console.log("disabled")
    CF._disable(button)
  }
}

function update_selected_pn(op){
  // console.log("update_selected_pn:", op)
  let modal = null
  let select_wrapper = null
  let input_wrapper = null
  let dst_port_wrapper = null
  let new_dst_port_wrapper = null
  switch(op){
    case __LIGHTEDGE_WEBUI.MODAL.TYPE.ADD:
      modal = ADD_MODAL
      select_wrapper = $("#add_ip_proto_select_wrapper")
      input_wrapper = $("#add_ip_proto_num_wrapper")
      dst_port_wrapper = $("#add_dst_port_wrapper")
      new_dst_port_wrapper = $("#add_new_dst_port_wrapper")
      break
  }
  if (CF._is_there(modal)){
    let select = modal.ip_proto_select
    let input = modal.ip_proto_num

    input.set(select.get())

    let value = input.get()

    IP_PROTOCOL_SELECT_OPTIONS.some(function(elem){
      // console.log(elem.value, value)
      if ((""+elem.value) === (""+value)){
          // ALLOW PORTS
          enable_ports("ADD", elem.allow_port)
          if (elem.allow_port){
            dst_port_wrapper.removeClass("d-none")
            new_dst_port_wrapper.removeClass("d-none")
          }
          else{
            dst_port_wrapper.addClass("d-none")
            new_dst_port_wrapper.addClass("d-none")   
          }
          // CUSTOM option
          if (value === ""){
            CF._enable(input.$instance)
            select_wrapper.removeClass("col-8 pr-0")
            select_wrapper.addClass("col-4 pr-1")
            input_wrapper.removeClass("d-none")
          }
          else{
            CF._disable(input.$instance)
            select_wrapper.addClass("col-8 pr-0")
            select_wrapper.removeClass("col-4 pr-1")
            input_wrapper.addClass("d-none")
          }
          return true
      }
    })
  }
}

function enable_ports(op, enable){
  let modal = null
  switch(op){
    case "ADD":
      modal = ADD_MODAL
      break
  }
  if (CF._is_there(modal)){
    let port = modal.dst_port
    let new_port = modal.new_dst_port
    if (enable){
      console.log("enabling",op,enable)
      CF._enable(port.$instance)
      CF._enable(new_port.$instance)
    }
    else{
      console.log("disabling",op,enable)
      port.set(DEFAULT_DESTINATION_PORT_VALUE)
      new_port.set(DEFAULT_NEW_DESTINATION_PORT_VALUE)

      CF._disable(port.$instance)
      CF._disable(new_port.$instance)

    }
   

  }
}

function mismatch_alert_generate_warning(...args) {

    matches = args[0]["matches"]
    missing_match = args[0]["missing_match"]
    extra_match = args[0]["extra_match"]
    messed_match = args[0]["messed_match"]

    if (CF._is_there(missing_match) &&
        CF._is_there(extra_match) &&
        CF._is_there(messed_match)){

        alert_strong_text = "Misalignment detected between Main and Local Matchlists."
        alert_text = ""

        if (missing_match){
            alert_text += "<br>Some main matches are not yet present at local level."
        }
        else if (extra_match){
            alert_text += "<br>Some local matches are not present at main level."
        }
        else if (messed_match){
            alert_text += "<br>Match order at local levels is different from the one at main level."
        }

        if (alert_text != ""){
            alert_text += "<br>It should be a temporary situation: try refreshing table to check if it has been solved"
            new WEBUI_Alert_Warning("alert_" + lightedge_alert_assign_id_number(),
                                alert_strong_text,
                                alert_text)
            .generate().show()
        }
        else{
            new WEBUI_Alert_Success("alert_" + lightedge_alert_assign_id_number(),
                                "Main and local match lists are consistent",
                                "")
            .generate().show()
        }
    }
    else{
        console.warn("missing response fields ", args)
    }
  
    
  }