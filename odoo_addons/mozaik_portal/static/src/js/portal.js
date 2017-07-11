openerp.mozaik_portal = function(instance) {

    var _super_do_action = instance.web.ActionManager.prototype.do_action;

    instance.web.ActionManager.include({
        init : function() {
            this._super.apply(this, arguments);
        },
        do_action : function(action, options) {
            var parent = this; 
            var ncontext= new instance.web.CompoundContext(action.context);
            var context = instance.web.pyeval.eval('context', ncontext);
            if (context && context.default_open_partner_user){
                var res_model = 'res.users';
                model = new instance.web.Model(res_model);
                model.call('read', {
                    ids : parent.session.uid,
                    fields : [ 'partner_id' ]
                }).then(function(result) {
                    action.res_id = result.partner_id[0];
                    return _super_do_action.call(parent, action, options);
                });
            }
            return this._super.apply(this, arguments);

        }
    });
};
