$(document).ready(function() {
  refresh_maps();
});

function refresh_maps() {

  update_uemaps = function(data){
    uemaps = 0
    if ((data === undefined)||(data===null)){
        data = {}
    }
    for (var key in data){
        if (data[key] != null)
            uemaps += Object.keys(data[key]).length
    }  
    // $("#uemap").text(Object.keys(data).length)
    $("#uemap_summary").text(uemaps)
  }

  update_matchmaps = function(data){
    $("#matchmap_summary").text(data.length)
  }

  update_upfclients = function(data){
    $("#upfclient_summary").text(Object.keys(data).length)
  }

  REST_REQ( __LIGHTEDGE_WEBUI.ENTITY.UEMAP).configure_GET({
    success: [ lightedge_log_response, update_uemaps],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()

  REST_REQ( __LIGHTEDGE_WEBUI.ENTITY.MATCHMAP).configure_GET({
    success: [ lightedge_log_response, update_matchmaps],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()

  REST_REQ( __LIGHTEDGE_WEBUI.ENTITY.UPFCLIENT).configure_GET({
    success: [ lightedge_log_response, update_upfclients],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()
}
