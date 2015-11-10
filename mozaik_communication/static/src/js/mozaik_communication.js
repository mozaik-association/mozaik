openerp.mozaik_communication = function(instance) {
    "use strict";
    var BYPASS_MODEL_BUTTON_DISABLE = ['virtual.target'];
    instance.web.list.Button.include({
        format : function(row_data, options) {
            var self = this;
            var res = self._super(row_data, options);
            if($.inArray(options.model, BYPASS_MODEL_BUTTON_DISABLE) != -1){
                var $res = $(res);
                $res.removeAttr('disabled');
                $res.removeClass('oe_list_button_disabled');
                res = $res.prop('outerHTML');
            }
            return res;
        },
    });
};
