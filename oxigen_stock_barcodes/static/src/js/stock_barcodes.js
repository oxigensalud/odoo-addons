/* Copyright 2021 ForgeFlow S.L.
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define("oxigen_stock_barcodes.ControlPanel", function(require) {
    "use strict";

    var ControlPanel = require("web.ControlPanel");

    ControlPanel.include({
        _render_breadcrumbs_li: function(bc, index, length) {
            /*
            If title in the breadcrumb is too long, the full form can overflow
            when the title gets refreshed from "New" to the real name (e.g.
            clicking a action button).
            We take only the first word to prevent this overflow from happening.
            Migration Note: likely not needed in versions >11.0
            */
            if (
                !bc.action.action_descr.res_model.includes("wiz.stock.barcodes.read.")
            ) {
                return this._super(bc, index, length);
            }
            var self = this;
            var is_last = index === length - 1;
            var li_content = bc.title && _.escape(bc.title.trim());
            // Only change from original function is next line:
            li_content = li_content.split(" ")[0];
            var $bc = $("<li>")
                .append(is_last ? li_content : $("<a>").html(li_content))
                .toggleClass("active", is_last);
            if (!is_last) {
                $bc.click(function() {
                    self.trigger("on_breadcrumb_click", bc.action, bc.index);
                });
            }
            return $bc;
        },
    });
});
