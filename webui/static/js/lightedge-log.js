/**
 * Class WEBUI_Log is a support class for logging
 * 
 */


__LIGHTEDGE_WEBUI.LOG={
  INSTANCE: null,
  ENABLED:{
    HTTP_RESPONSE: true
  }
}
/**
 * This function is just printing out all its arguments.
 * Can be useful for debugging purposes if added among the success / error / 
 * complete functions in a jQuery ajax request, to display what returned by the 
 * request
 * 
 * @param  {...any} args - argument of the function (kept generic in order to 
 *                         process them dinamically inside the function)
 */
function lightedge_log_response(...args) {
  if (__LIGHTEDGE_WEBUI.LOG.ENABLED.HTTP_RESPONSE){
    console.log("HTTP_RESPONSE LOG: ")
    args.forEach(function(arg, index){
      console.log("args["+index+"] (type:",(typeof arg),"): ",arg)
    })
  }
}