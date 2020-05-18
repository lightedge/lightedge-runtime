$('#upfmanager').removeClass('collapsed');
$('#collapse_upfmanager').addClass('show');
$('#upfclient').addClass('active');

// $(document).ready(function() {

//   aoColumns = [
//           { "sTitle": "Address" },
//           { "sTitle": "Description" },
//           { "sTitle": "Last seen" },
//           { "sTitle": "Address" },
//   ]

//   t = $('#dataTable').DataTable({
//       "aoColumns": aoColumns
//   });

//   refresh();

// });


// function refresh() {

// }

PROT_PORT_SUPP = {6: "tcp", 17: "udp", 132: "sctp"}

console.log("__LIGHTEDGE_WEBUI",__LIGHTEDGE_WEBUI)

$(document).ready(function() {

  ENTITY = __LIGHTEDGE_WEBUI.ENTITY.UPFCLIENT

  // MODAL_FIELD__ADDRESS= "address"
  // MODAL_FIELD__DESCRIPTION= "desc"

  let fields = {
    address: {
      type: "TEXT"
    },
    desc: {
      type: "TEXT"
    },
  }

  // ADD_MODAL = new WEBUI_Modal_Entity(
  //   __LIGHTEDGE_WEBUI.MODAL.TYPE.ADD,
  //   ENTITY
  // ).add_fields(fields)

  // EDIT_MODAL = new WEBUI_Modal_Entity(
  //   __LIGHTEDGE_WEBUI.MODAL.TYPE.EDIT,
  //   ENTITY
  // ).add_fields(fields)

  // REMOVE_MODAL = new WEBUI_Modal_Entity(
  //   __LIGHTEDGE_WEBUI.MODAL.TYPE.REMOVE,
  //   ENTITY
  // ).add_fields(fields)

  aoColumns = [
    // { "sTitle": "ID" },
    { "sTitle": "TAG" },
    { "sTitle": "Remote Addr:Port" },
    // { "sTitle": "UE Map" },
    { "sTitle": "Local Matches" },
    { "sTitle": "Status" },
    
  ]

  DATATABLE = $('#dataTable').DataTable({
  "aoColumns": aoColumns
  });

  refresh_datatable();
});

ENTITY = null

function add() {

  let data = {
    "version":"1.0",
    "addr": ADD_MODAL.address.get(),
    "desc": ADD_MODAL.desc.get()
  }

  console.log("data: ",data)
  
  add_reset = ADD_MODAL.reset.bind(ADD_MODAL)

  REST_REQ(ENTITY).configure_POST({
    data: data,
    success: [ lightedge_log_response, lightedge_alert_generate_success, 
      add_reset, refresh_datatable ],
    error: [ lightedge_log_response, lightedge_alert_generate_error ]
  })
  .perform()

}

function trigger_edit_modal( wtp_key ) {

  show_edit_modal = function(data){

    EDIT_MODAL.address.set(data.addr)
    EDIT_MODAL.desc.set(data.desc)

    EDIT_MODAL.get_$instance().modal({show:true})
  }

  REST_REQ(ENTITY).configure_GET({
    key: wtp_key,
    success: [ lightedge_log_response, show_edit_modal],
    error: [ lightedge_log_response, lightedge_alert_generate_error ]
  })
  .perform()
}

function edit(){

  let data = {
    "version":"1.0",
    "addr": EDIT_MODAL.address.get(),
    "desc": EDIT_MODAL.desc.get()
  }
  
  edit_reset = EDIT_MODAL.reset.bind(EDIT_MODAL)

  REST_REQ(ENTITY).configure_PUT({
    data: data,
    key: data.addr,
    success: [ lightedge_log_response, lightedge_alert_generate_success, 
      edit_reset, refresh_datatable ],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()
}

function trigger_remove_modal( wtp_key ) {

  show_remove_modal = function(data){

    REMOVE_MODAL.address.set(data.addr)
    REMOVE_MODAL.desc.set(data.desc)

    REMOVE_MODAL.get_$instance().modal({show:true})
  }

  REST_REQ(ENTITY).configure_GET({
    key: wtp_key,
    success: [ lightedge_log_response, show_remove_modal],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()
}

function remove(){

  let key = REMOVE_MODAL.address.get()
  
  REMOVE_MODAL.reset()

  REST_REQ(ENTITY).configure_DELETE({
    key: key,
    success: [
      lightedge_log_response, lightedge_alert_generate_success, refresh_datatable ],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()
}

function format_datatable_data( data ) {

  console.log("DATA: ", data)

  $.each( data, function( key, val ) {

    DATATABLE.row.add([
        // val['id'],
        val['tag'],
        val['remote_address']+":"+val['remote_port'],
        // val['uemap'],
        // Object.keys(val['local_matches']).length,
        format_match_field(val),
        format_status_field(val["status"])
    ] )

  });

  DATATABLE.draw(true)

}

function format_status_field(status){
    if (status === "consistent"){
        return '<div class="d-flex justify-content-center"><i class="fas fa-check-circle fa-2x fa-fw text-success"></i></div>'
    }
    else{
        return '<div class="d-flex justify-content-center"><i class="fas fa-times-circle fa-2x fa-fw text-danger"></i></div>'
    }
}

function format_match_field(data){

    matches = data['local_matches']

    upf_client_id = self.generate_upf_client_id(data)
    
    html = ""
    match_number = Object.keys(matches).length
    html += '<div class="mt-1">' + match_number + " Match"
    if (match_number != 1){
        html += "es"
    }
    html += "</div>"
    html += ""+
      '<button class="btn btn-sm btn-info shadow-sm m-0" '+
      'onclick="toggle_match_visualization(\''+ upf_client_id +'\')">'+
      '<i class="fas fa-eye fa-sm fa-fw text-white-50 mr-xl-1 mt-1"></i><span class="d-none d-xl-inline">Show</span></button>'

    mid = 
    html = '<div class="d-flex justify-content-between">' + html + "</div>"

    html += '<div id=' + upf_client_id +' class="d-none mt-3">'

    $.each( matches, function( key, val ) {
        forwarding = "" + val["dst_ip"] + "/" + val["netmask"]
        console.log(val["dst_port"])
        if (val["dst_port"] != 0){
            forwarding += ":" + val["dst_port"]
        }
        forwarding += "(prot: " + val["ip_proto_num"] + ")"
        rewriting = ""
        if (val["new_dst_ip"] != null){
            rewriting = "--> " + val["new_dst_ip"]
            if (val["new_dst_port"] != 0){
                rewriting += ":" + val["new_dst_port"]
            }
        }
        description = val["desc"]
        uuid = val["uuid"]
        html += '<div class="form-group row border-top m-1">'
        html +=    '<div class="col-2 text-center font-weight-bold mt-1">'
        html +=        '<span>' + (key+1) +'</span>'
        html +=    '</div>'
        html +=    '<div class="col-10">'
        html +=        '<div class="text-left col-12 small mt-1">' + forwarding + '</div>'
        if (rewriting != ""){
            html +=    '<div class="text-left col-12 small">' + rewriting + '</div>'
        }
        html +=        '<div class="text-left col-12 text-xs">' + description + '</div>'
        html +=        '<div class="text-left col-12 text-xs text-gray-500">' + uuid + '</div>'
        html +=    '</div>'
        html += '</div>'
    })

    html += '</div>'
    
    return html
}

function toggle_match_visualization(upf_client_id){
    $('#'+upf_client_id).toggleClass("d-none")
}

function generate_upf_client_id(data){
    return data['tag']//+"_"+data['remote_address']+"_"+data['remote_port']
}

function refresh_datatable() {

  DATATABLE.clear();
  // if(__LIGHTEDGE_WEBUI.TEST){
  //   REST_REQ(ENTITY).configure_GET({
  //     success: [ format_datatable_data ],
  //     error: [ format_datatable_data ]
  //   })
  //   .perform()
  //   return
  // }
  REST_REQ(ENTITY).configure_GET({
    success: [ lightedge_log_response, format_datatable_data],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()

  
}