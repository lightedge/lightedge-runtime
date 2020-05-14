$('#upfmanager').removeClass('collapsed');
$('#collapse_upfmanager').addClass('show');
$('#uemap').addClass('active');

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


console.log("__LIGHTEDGE_WEBUI",__LIGHTEDGE_WEBUI)

$(document).ready(function() {

  ENTITY = __LIGHTEDGE_WEBUI.ENTITY.UEMAP

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
    { "sTitle": "UE IP" },
    { "sTitle": "eNB IP" },
    { "sTitle": "TEID UPLINK" },
    { "sTitle": "EPC IP" },
    { "sTitle": "TEID DOWNLINK" },
    { "sTitle": "UPF Client" },
    // { "sTitle": "Actions", "sClass": "text-center" }
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

  $.each( data, function( upf_client_id, uemap ) {
    $.each( uemap, function( key, val ) {

        actions = ""+
        '<button class="btn btn-sm btn-warning shadow-sm mr-xl-1 mb-md-1 m-1" '+
        'onclick="trigger_edit_modal(\''+val['addr']+'\')">'+
        '<i class="fas fa-edit fa-sm fa-fw text-white-50 mr-xl-1 m-1"></i><span class="d-none d-xl-inline">Edit</span></button>'+
        '<button class="btn btn-sm btn-danger shadow-sm mb-xl-1 m-1" '+
        'onclick="trigger_remove_modal(\''+val['addr']+'\')">'+
        '<i class="fas fa-trash fa-sm fa-fw text-white-50 mr-xl-1 m-1"></i><span class="d-none d-xl-inline">Remove</span></button>'

        DATATABLE.row.add([
            val['ue_ip'],
            val['enb_ip'],
            val['teid_uplink'],
            val['epc_ip'],
            val['teid_downlink'],
            upf_client_id,
            // actions
        ] )

    });
  });

  DATATABLE.draw(true)

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