odoo.define('distribution_list.distribution_list', function (require) {
"use strict";

var core = require('web.core');
var dialogs = require('web.view_dialogs');
var FormController = require("web.FormController")

var _t = core._t;

var distribution_list = dialogs.SelectCreateDialog.extend({

    custom_events: _.extend({}, dialogs.SelectCreateDialog.prototype.custom_events, {
        select_record: function (event) {
            event.stopPropagation();// do nothing when record is clicked
        },
        open_record: function (event) {
            event.stopPropagation();// do nothing when record is clicked
        },
        search: function(event) {
            // store the domain of the search
            this.search_domain = event.data.domains[0]

            //copied from view_dialogs.js
            event.stopPropagation(); // prevent this event from bubbling up to the view manager
            var d = event.data;
            var searchData = this._process_search_data(d.domains, d.contexts, d.groupbys);
            this.list_controller.reload(searchData);
            //end copied
        }
    }),

    init: function () {
        this._super.apply(this, arguments);
        this.record = this.options.record;
        this.reload_fnct = this.options.reload_fnct;
    },

    setup: function (search_defaults, fields_views) {
        var self = this
        var res = this._super.apply(this, arguments).then(function (fragment) {
            self.__buttons.unshift({
                text: _t("Save Expression"),
                classes: "btn-primary",
                click: self.save_domain,
            });
            return fragment
        });
        return res
    },

    save_domain: function() {
        /*
        * pre: item is initialized and contain the item clicked
        * post: the view is closed
        * res: the 'save_domain' method is called from the model
        *      'distribution.list.line'
        */
        var res_id = this.record.res_id;
        var domain = this.search_domain || [];
        var self = this;
        this._rpc({
            model: 'distribution.list.line',
            method: 'save_domain',
            args: [[res_id], domain],
            }).then(function(result) {
                self.reload_fnct();
                self.close();
            });
    },
})

FormController.include({
    _onButtonClicked: function (event) {
        if (event.data.attrs.name == "action_redefine_domain") {
            event.stopPropagation();
            var self = this
            new distribution_list(this, {
                record: event.data.record, // current record
                res_model: event.data.record.data.src_model_model, // model to search
                reload_fnct: function() {self.reload()}, // refresh the form when the domain is changed
                no_create: true, // hide create button
                disable_multiple_selection: true, // hide checkbox
            }).open();
        }
        else{
            this._super.apply(this, arguments);
        }
    },
});

});
