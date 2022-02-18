odoo.define('account_parent.AbstractAction', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ActionMixin = require('web.ActionMixin');

	AbstractAction.include({
		on_attach_callback: function () {
	        ActionMixin.on_attach_callback.call(this);
			console.log("Hum Aapke hain kon")
			if (this.searchModel){
	        	this.searchModel.on('search', this, this._onSearch);
			}
	        if (this.hasControlPanel) {
	            this.searchModel.on('get-controller-query-params', this, this._onGetOwnedQueryParams);
	        }
	    },
		on_detach_callback: function () {
	        ActionMixin.on_detach_callback.call(this);
			if (this.searchModel){
	        	this.searchModel.off('search', this);
			}
	        if (this.hasControlPanel) {
	            this.searchModel.off('get-controller-query-params', this);
	        }
	    },
	})
});