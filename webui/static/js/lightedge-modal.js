__LIGHTEDGE_WEBUI.MODAL={
  TYPE:{
    ADD: "ADD",
    EDIT: "EDIT",
    REMOVE: "REMOVE",
    GENERIC: "GENERIC"
  },
  PREFIX:{
    ADD: "add_",
    EDIT: "edit_",
    REMOVE: "remove_",
    GENERIC: ""
  },
  SUFFIX:{
    MODAL: "_Modal",
  },
  FIELD:{
    TYPE:{
      TEXT: "TEXT",
      CHECKBOX: "CHECKBOX",
      SELECT: "SELECT",
      SELECT_OWNER: "SELECT_OWNER"
    }
  }
}

class WEBUI_Modal extends WEBUI_CoreFunctions{
  constructor(modal_type, modal_id){
    super()
    if (!this.verify_modal_type(modal_type)){
      console.error("INVALID Modal Type: potential issues")
    }
    this._TYPE = modal_type
    this._ID = modal_id
    this._$INSTANCE = $("#"+modal_id)
    if (!this.check_consistency()){
      console.error("CONSISTENCY CHECK FAILED: potential issues")
    }
  }

  get_modal_id(){
    return this._ID
  }

  get_modal_type(){
    return this._TYPE
  }
  get_$instance(){
    return this._$INSTANCE
  }

  verify_modal_type(modal_type){
    switch(modal_type){
      case __LIGHTEDGE_WEBUI.MODAL.TYPE.ADD:
      case __LIGHTEDGE_WEBUI.MODAL.TYPE.EDIT:
      case __LIGHTEDGE_WEBUI.MODAL.TYPE.REMOVE:
      case __LIGHTEDGE_WEBUI.MODAL.TYPE.GENERIC:
        return true
    }
    console.error("UNKNOWN Modal Type: ", modal_type)
    return false
  }

  check_consistency(){
    if (this._is_there(this.get_$instance())){
      if (this.get_$instance().length > 0){
        if(this.get_$instance().length === 1){
          return true
        }
        else{
          console.error("MORE THAN 1 elements with modal identifier found! (",
          this.get_modal_id(),")" )
        }
      }
      else{
        console.error("NO elements with modal identifier found! (",
                      this.get_modal_id(),")" )
      }
    }
    else{
      console.error("$INSTANCE NOT SET")
    }
    return false
  }

  add_fields(field_dictionary, apply_modal_type_prefix=true){
    this._FIELDS = {}
    if (this._is_object(field_dictionary)){
      $.each(field_dictionary, function( key, val ) {
        let fkey = key
        if (apply_modal_type_prefix){
          fkey = this.apply_field_prefix(key)
          // console.log("fkey", fkey)
        }

        this._FIELDS[fkey]= this.retrieve_modal_field(val.type, fkey)
        if(this._is_there(val.default)){
          this._FIELDS[fkey].set_value(val.default)
        }

        this.configure_field_dedicated_methods(key, fkey)

      }.bind(this))
    }

    return this
  }

  apply_field_prefix(key, modal_type=null){
    if (!this._is_there(modal_type)){
      modal_type = this.get_modal_type()
    }
    switch(modal_type){
      case __LIGHTEDGE_WEBUI.MODAL.TYPE.ADD:
        return __LIGHTEDGE_WEBUI.MODAL.PREFIX.ADD + key
      case __LIGHTEDGE_WEBUI.MODAL.TYPE.EDIT:
        return __LIGHTEDGE_WEBUI.MODAL.PREFIX.EDIT + key
      case __LIGHTEDGE_WEBUI.MODAL.TYPE.REMOVE:
        return __LIGHTEDGE_WEBUI.MODAL.PREFIX.REMOVE + key
      case __LIGHTEDGE_WEBUI.MODAL.TYPE.GENERIC:
        return __LIGHTEDGE_WEBUI.MODAL.PREFIX.GENERIC + key
    }
    console.warn("NO PREFIX FOUND for modal type:", modal_type)
    return key
  }

  retrieve_modal_field(field_type, field_id){
    switch(field_type){
      case __LIGHTEDGE_WEBUI.MODAL.FIELD.TYPE.TEXT:
        return new WEBUI_ModalField_Text(field_id)
      case __LIGHTEDGE_WEBUI.MODAL.FIELD.TYPE.CHECKBOX:
        return new WEBUI_ModalField_CheckBox(field_id)
      case __LIGHTEDGE_WEBUI.MODAL.FIELD.TYPE.SELECT:
        return new WEBUI_ModalField_Select(field_id)
      case __LIGHTEDGE_WEBUI.MODAL.FIELD.TYPE.SELECT_OWNER:
        return new WEBUI_ModalField_SelectOwner(field_id)
      default:
        console.error("UNKNOWN Modal field type: ", field_type)
        return null
    }
  }

  configure_field_dedicated_methods(key, fkey){
    if (this._is_there(this[key])){
      console.error("CONFLICT with existent method with key: ", key,
                    "\nDisruptive malfunctionings may occur!")
    }
    else{
      this[key] = {}
      this[key].get = this._FIELDS[fkey].get_value.bind(this._FIELDS[fkey])
      this[key].set = this._FIELDS[fkey].set_value.bind(this._FIELDS[fkey])
      this[key].reset = this._FIELDS[fkey].reset.bind(this._FIELDS[fkey])
      this[key].$instance = this._FIELDS[fkey].get_$instance()
      this[key].on_change = this[key].$instance.change.bind(this[key].$instance)
    }
    return this
  }

  reset(defaults={}){
    // console.log("defaults =",defaults)
    let prefix_length = __LIGHTEDGE_WEBUI.MODAL.PREFIX[this._TYPE].length
    $.each(this._FIELDS, function( key, val ) {
      // console.log(key,)
      let def_key = key.substring(prefix_length)
      // console.log(def_key)
      if (this._is_there(defaults) &&
          this._is_there(defaults[def_key])){
        if (this._is_there(defaults[def_key].value)){
          // console.log("reset key", key,"to", defaults[def_key].value)
          if (this._is_there(defaults[def_key].options)){
            val.reset(defaults[def_key].options, defaults[def_key].value)
          }
          else{
            val.reset(defaults[def_key].value)
          }
        }
      }
      else{
        val.reset()
      }
    })
  }

  show(){
    // this.get_$instance().modal({show:true})
    this.get_$instance().modal('show')

    return this
  }

  hide(){
    this.get_$instance().modal('hide')

    return this
  }

}


class WEBUI_Modal_Entity extends WEBUI_Modal{
  constructor( modal_type, entity){
    let modal_id = __LIGHTEDGE_WEBUI.MODAL.PREFIX[modal_type] +
                   entity +
                   __LIGHTEDGE_WEBUI.MODAL.SUFFIX.MODAL

    // console.log("modal_id= ", modal_id)
    super(modal_type, modal_id)

  }
}


class WEBUI_ModalField extends WEBUI_CoreFunctions{
  constructor(field_id){
    super()

    // console.log("field_id:", field_id)

    this._ID = field_id
    this._$INSTANCE = $("#"+field_id)
    if (!this.check_consistency()){
      console.error("CONSISTENCY CHECK FAILED: potential issues")
    }

  }

  get_field_id(){
    return this._ID
  }

  get_$instance(){
    return this._$INSTANCE
  }

  check_consistency(){
    if (this._is_there(this.get_$instance())){
      if (this.get_$instance().length > 0){
        if(this.get_$instance().length === 1){
          return true
        }
        else{
          console.error("MORE THAN 1 elements with field identifier found! (",
                        this.get_field_id(),")" )
        }
      }
      else{
        console.error("NO elements with field identifier found! (",
                      this.get_field_id(),")" )
      }
    }
    else{
    console.error("$INSTANCE NOT SET")
    }
    return false
  }

  set_value(value){
    console.warn("Method  'set_value' to be overridden")
    return this

  }

  get_value(){
    console.warn("Method 'get_value' to be overridden")
    return null
  }

  reset(value){
    console.warn("Method 'reset' to be overridden")
    return this
  }

  disable(){
    this._$INSTANCE.prop("disabled", true)
  }

  get_default(){
    // console.log(this._$INSTANCE)
    return this._$INSTANCE.attr("default")
  }

}

class WEBUI_ModalField_Text extends WEBUI_ModalField{
  constructor(field_id){
    super(field_id)
  }

  set_value(value){
    this.get_$instance().val(value)
  }

  get_value(){
    return this.get_$instance().val()
  }

  reset(value){
    // console.log("reset to ", value)
    this.set_value("")
    if (this._is_there(value)){
      this.set_value(value)
    }
    return this
  }
}

class WEBUI_ModalField_CheckBox extends WEBUI_ModalField{
  constructor(field_id){
    super(field_id)
  }

  set_value(value){
    this.get_$instance().prop("checked",value)
  }

  get_value(){
    return this.get_$instance().prop("checked")
  }

  reset(value=false){
    // console.log("reset to ", value)
    this.set_value(false)
    if (this._is_there(value)){
      this.set_value(value)
    }
    return this
  }
}

class WEBUI_ModalField_Select extends WEBUI_ModalField{
  constructor(field_id){
    super(field_id)
    // console.log("modal_field_SELECT")
  }

  set_value(value){
    this.get_$instance().val(value)
  }

  get_value(){
    return this.get_$instance().val()
  }

  reset(options, value=0){
    this.reset_options_from_descriptor(options)
    if (this._is_there(value)){
      this.set_value(value)
    }
    return this
  }

  add_option(label, value){
    this.get_$instance().append(
      new Option(label, value))
  }

  reset_options_from_descriptor(descriptor){
    // descriptor structure:
    // [
    //   {
    //     label: "label1",
    //     value: "value1"
    //   }
    //   ...
    // ]
    if (!this._is_there(descriptor)){
      descriptor = []
    }
    this.get_$instance().empty()
    descriptor.forEach(function(item){
      this.add_option(item.label, item.value)
    }, this)
  }
}

