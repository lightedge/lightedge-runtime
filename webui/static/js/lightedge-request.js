

/**
 * Class WEBUI_Request provides a manager for HTTP asynchronous requests for the 
 * WEBUI.
 * 
 * 
 * @extends WEBUI_CoreFunctions
 * 
 */
class WEBUI_Request extends WEBUI_CoreFunctions{

  // _ENTRY_POINT = 'http://upf-service.default.of.empower:80/upf/v1/'
  _ENTRY_POINT = '/upf/v1/'
  _REQ_TIMEOUT_INTERVAL = 2000 //ms

  /**
   * Constructor
   * 
   */
  constructor() {

    super()

    this._CLASSNAME = this.constructor.name

    this.REQUEST = null

  }

  /**
   * This method configures the asynchronous HTTP request (ajax) according 
   * to the params passed
   * 
   * @param {Object} options - All the configuration options.
   * @param {?string} options.method - The HTTP method to use for the request.
   * @param {?string} options.dataType - The type of data that expected back 
   *                                     from the server.
   * @param {?(Object|string)} options.data - Data to be sent to the server.
   * @param {?boolean} options.cache - If set to false, it will force requested 
   *                                   pages not to be cached by the browser.
   * @param {?function[]} options.success - A sequence of functions to be called
   *                                        if the request succeeds.
   * @param {?function[]} options.complete - A sequence of functions to be 
   *                                        called when the request finishes 
   *                                        (after success and error callbacks 
   *                                        are executed).
   * @param {?function[]} options.error - A sequence of functions to be called 
   *                                      if the request fails.
   * @param {?number} options.timeout - Set a timeout (in milliseconds) for the 
   *                                    request. A value of 0 means there will 
   *                                    be no timeout.
   * @param {?boolean} options.auth_requested - true if authentication is 
   *                                            required, false otherwise.
   * @param {?Object|string} options.key - a parameter identifying the specific 
   *                                      target of the request
   * 
   * @return {Object} current WEBUI_Request instance
   */
  configure({ method = "GET",
    dataType = "json", data = {},
    cache = false,
    success = [], error = [], complete = [],
    timeout = this._REQ_TIMEOUT_INTERVAL,
    key = null
  }) {

    this.REQUEST = {
      method: method,
      url: this.get_URL(method, key),
      dataType: dataType,
      data: this.get_formatted_data(data, method),
      cache: cache,
      timeout: timeout,
      success: success,
      error: error,
      complete: complete,
      // crossDomain: true
      headers:{
        // "Access-Control-Allow-Origin": "*",
        // "Access-Control-Allow-Methods": "POST, DELETE, GET, OPTIONS"
      }
    }

    this.REQUEST.beforeSend = function (req) {
      // console.log("Allowing CORS")
      // req.setRequestHeader("Access-Control-Allow-Origin", "*");
      req.lightedge = {
        url: this.REQUEST.url,
        method: this.REQUEST.method,
        data: this.REQUEST.data,
        time_ts: Date.now(),
        time: new Date().toISOString()
      }
    }.bind(this)


    // console.log(this._CLASSNAME, " CONFIGURE req:", this.REQUEST)

    return this
  }

  /**
   * This method returns the data properly formatted for the associated HTML
   *  Request type
   * 
   * @param {?(Object|string)} data 
   * @param {string} method 
   * 
   * @return {string} data formatted for request
   */
  get_formatted_data(data, method = GET) {
    if (!this._is_there(data)) {
      return ""
    }
    else if (this._is_string(data)) {
      return data
    }
    else {
      return JSON.stringify(data)
    }
  }

  /**
   * 
   * @param {string} method 
   * @param {Object|string} key 
   */
  get_URL(method, key) {
    return this._ENTRY_POINT
  }

  /**
   * This method configures the asynchronous GET HTTP request (ajax) 
   * according to the params passed
   * 
   * @param {Object} options - All the configuration options.
   * @param {?function[]} options.success - A sequence of functions to be called
   *                                        if the request succeeds.
   * @param {?function[]} options.complete - A sequence of functions to be 
   *                                        called when the request finishes 
   *                                        (after success and error callbacks 
   *                                        are executed).
   * @param {?function[]} options.error - A sequence of functions to be called 
   *                                      if the request fails.
   * @param {?number} options.timeout - Set a timeout (in milliseconds) for the 
   *                                    request. A value of 0 means there will 
   *                                    be no timeout.
   * @param {?Object|string} options.key - a parameter identifying the specific 
   *                                      target of the request
   * 
   * @return {Object} current WEBUI_Request instance
   */
  configure_GET({ cache = false,
    success = [], error = [], complete = [],
    timeout = this._REQ_TIMEOUT_INTERVAL,
    key = null
  }) {
    return this.configure({
      method: "GET",
      dataType: "json", data: "",
      cache: cache,
      success: success, error: error, complete: complete,
      timeout: timeout,
      key: key
    })
  }

  /**
   * This method configures the asynchronous POST HTTP request (ajax) 
   * according to the params passed
   * 
   * @param {Object} options - All the configuration options.
   * @param {?(Object|string)} options.data - Data to be sent to the server.
   * @param {?boolean} options.cache - If set to false, it will force requested 
   *                                   pages not to be cached by the browser.
   * @param {?function[]} options.success - A sequence of functions to be called
   *                                        if the request succeeds.
   * @param {?function[]} options.complete - A sequence of functions to be 
   *                                        called when the request finishes 
   *                                        (after success and error callbacks 
   *                                        are executed).
   * @param {?function[]} options.error - A sequence of functions to be called 
   *                                      if the request fails.
   * @param {?number} options.timeout - Set a timeout (in milliseconds) for the 
   *                                    request. A value of 0 means there will 
   *                                    be no timeout.
   * 
   * @return {Object} current WEBUI_Request instance
   */
  configure_POST({ cache = false,
    data = {},
    success = [], error = [], complete = [],
    timeout = this._REQ_TIMEOUT_INTERVAL,
    key = null
  }) {
    return this.configure({
      method: "POST",
      dataType: "text", data: data,
      cache: cache,
      success: success, error: error, complete: complete,
      timeout: timeout,
      key: key
    })
  }

  /**
   * This method configures the asynchronous PUT HTTP request (ajax) 
   * according to the params passed
   * 
   * @param {Object} options - All the configuration options.
   * @param {?(Object|string)} options.data - Data to be sent to the server.
   * @param {?boolean} options.cache - If set to false, it will force requested 
   *                                   pages not to be cached by the browser.
   * @param {?function[]} options.success - A sequence of functions to be called
   *                                        if the request succeeds.
   * @param {?function[]} options.complete - A sequence of functions to be 
   *                                        called when the request finishes 
   *                                        (after success and error callbacks 
   *                                        are executed).
   * @param {?function[]} options.error - A sequence of functions to be called 
   *                                      if the request fails.
   * @param {?number} options.timeout - Set a timeout (in milliseconds) for the 
   *                                    request. A value of 0 means there will 
   *                                    be no timeout.
   * @param {?Object|string} options.key - a parameter identifying the specific 
   *                                      target of the request
   * 
   * @return {Object} current WEBUI_Request instance
   */
  configure_PUT({ cache = false,
    data = {},
    success = [], error = [], complete = [],
    timeout = this._REQ_TIMEOUT_INTERVAL,
    key = null
  }) {

    return this.configure({
      method: "PUT",
      dataType: "text", data: data,
      cache: cache,
      success: success, error: error, complete: complete,
      timeout: timeout,
      key: key
    })
  }

  /**
   * This method configures the asynchronous DELETE HTTP request (ajax) 
   * according to the params passed
   * 
   * @param {Object} options - All the configuration options.
   * @param {?boolean} options.cache - If set to false, it will force requested 
   *                                   pages not to be cached by the browser.
   * @param {?function[]} options.success - A sequence of functions to be called
   *                                        if the request succeeds.
   * @param {?function[]} options.complete - A sequence of functions to be 
   *                                        called when the request finishes 
   *                                        (after success and error callbacks 
   *                                        are executed).
   * @param {?function[]} options.error - A sequence of functions to be called 
   *                                      if the request fails.
   * @param {?number} options.timeout - Set a timeout (in milliseconds) for the 
   *                                    request. A value of 0 means there will 
   *                                    be no timeout.
   * @param {?Object|string} options.key - a parameter identifying the specific 
   *                                      target of the request
   * 
   * @return {Object} current WEBUI_Request instance
   */
  configure_DELETE({ cache = false,
    success = [], error = [], complete = [],
    timeout = this._REQ_TIMEOUT_INTERVAL,
    key = null
  }) {
    return this.configure({
      method: "DELETE",
      dataType: "json", data: "",
      cache: cache,
      success: success, error: error, complete: complete,
      timeout: timeout,
      key: key
    })
  }

  /**
   * This method performs the currently configured (this._REQUEST) 
   * asynchronous HTTP request
   */
  perform() {
    console.log(this._CLASSNAME, " PERFORM req:", this.REQUEST)
    $.ajax(this.REQUEST)
  }
}

/**
 * Support global variable for storing the "entities" of LIGHTEDGE and refer them 
 * univocally in the WEBUI
 */
__LIGHTEDGE_WEBUI.ENTITY={
  UEMAP: "UEMAP",
  MATCHMAP: "MATCHMAP",
  UPFCLIENT: "UPFCLIENT"
}

/**
 * Class WEBUI_Request_ACCOUNT extends WEBUI_Request to the ACCOUNT specific 
 * case. It is actually just an alias of the extended class
 * 
 * @extends {WEBUI_Request}
 */
class WEBUI_Request_UEMAP extends WEBUI_Request {

  /**
   * @override
   */
  get_URL(method = "GET", key = null) {
    if (this._is_there(key)) {
      if ((method === "GET") ||
        (method === "PUT") ||
        (method === "DELETE")) {
        return this._ENTRY_POINT + "uemap/" + key
      }
    }
    return this._ENTRY_POINT + "uemap"
  }

}

/**
 * Class WEBUI_Request_ACCOUNT extends WEBUI_Request to the ACCOUNT specific 
 * case. It is actually just an alias of the extended class
 * 
 * @extends {WEBUI_Request}
 */
class WEBUI_Request_UPFCLIENT extends WEBUI_Request {

    /**
     * @override
     */
    get_URL(method = "GET", key = null) {
      if (this._is_there(key)) {
        if ((method === "GET") ||
          (method === "PUT") ||
          (method === "DELETE")) {
          return this._ENTRY_POINT + "client/" + key
        }
      }
      return this._ENTRY_POINT + "client"
    }
  
  }

/**
 * Class WEBUI_Request_PROJECT extends WEBUI_Request to the PROJECT specific 
 * case. It is actually just an alias of the extended class
 * 
 * @extends {WEBUI_Request}
 */
class WEBUI_Request_MATCHMAP extends WEBUI_Request {

  /**
   * @override
   */
  get_URL(method = "GET", key = null) {
    if (this._is_there(key)) {
      if ((method === "GET") ||
        (method === "POST") ||
        (method === "PUT") ||
        (method === "DELETE")) {
        return this._ENTRY_POINT + "matchmap/" + key
      }
    }
    return this._ENTRY_POINT + "matchmap"
  }

}


/**
 * Support factory for providing the proper WEBUI_Request_XXX class for the 
 * specified entity
 * 
 * @param {string} entity - identifier of the entity
 * 
 * @return {Object} An instance of the WEBUI_Request class (WEBUI_Request_XXX)
 *                  specific for the specified entity
 */
function REST_REQ(entity){
  switch(entity){
    case __LIGHTEDGE_WEBUI.ENTITY.UEMAP:
      return new WEBUI_Request_UEMAP()
    case __LIGHTEDGE_WEBUI.ENTITY.MATCHMAP:
      return new WEBUI_Request_MATCHMAP()
    case __LIGHTEDGE_WEBUI.ENTITY.UPFCLIENT:
      return new WEBUI_Request_UPFCLIENT()
    default:
      console.warn("Entity", 
        entity, 
        "unknown, default WEBUI_Request instance returned")
      return new WEBUI_Request()
  }
}

