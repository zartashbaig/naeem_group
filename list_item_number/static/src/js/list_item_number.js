odoo.define('list_item_number.ItemNumber', function (require) {
    'use strict';
    var core = require('web.core');
    var ListRenderer = require('web.ListRenderer');
    var _t = core._t;

    ListRenderer.include({
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            //line_section和line_note的行数
            this.skip_count = 0;
        },

        start: function () {
            var self = this;
            var reg = new RegExp("\\.", 'g');
            var model_name = this.state.model.replace(reg, '_');
            var model_css = 'o_' + model_name;
            return this._super().then(function () {
                self.$el.addClass(model_css);
            });
        },
        //为列表象增加编号No.
        _getNumberOfCols: function () {
            var columns = this._super();
            columns += 1;
            return columns;
        },

        _renderHeader: function (isGrouped) {
            var $header = this._super(isGrouped);
            if (this.hasSelectors) {
                $header.find('th.o_list_record_selector').before($('<th class="f_item_number">').html('No.')); //列表视图表头
            } else {
                if (this.mode !== 'edit') {
                    $header.find("tr").prepend($('<th class="f_item_number">').html('No.'));
                }
            }
            return $header;
        },

        _renderGroupRow: function (group, groupLevel) {
            var $row = this._super(group, groupLevel);
            if (this.mode !== 'edit' || this.hasSelectors) {
                $row.find("th.o_group_name").after($('<th class="f_item_blank">').html('&nbsp;')); //列表视图分组行
            }
            return $row;
        },

        _renderGroups: function (data, groupLevel) {
            var self = this;
            var _self = this;
            groupLevel = groupLevel || 0;
            var result = [
            ];
            var $tbody = $('<tbody>');
            _.each(data, function (group) {
                if (!$tbody) {
                    $tbody = $('<tbody>');
                }
                $tbody.append(self._renderGroupRow(group, groupLevel));
                if (group.data.length) {
                    result.push($tbody);
                    if (group.groupedBy.length) {
                        result = result.concat(self._renderGroups(group.data, groupLevel + 1));
                    } else {
                        var $records = _.map(group.data, function (record, index) {
                            if (_self.mode !== 'edit' || _self.hasSelectors) {
                                return self._renderRow(record).prepend($('<td class="f_item_number">').html(index + 1));
                            } else {
                                return self._renderRow(record).prepend($('<td>'));
                            }
                        });
                        result.push($('<tbody>').append($records));
                    }
                    $tbody = null;
                }
            });
            if ($tbody) {
                result.push($tbody);
            }
            return result;
        },
        _moveRecord: function (recordId, toIndex) {
            //recompute number
            this._super(...arguments)
            this._compute_line_no()

        },
        _compute_line_no: function ($node) {
            let index = 1;
            let $tdList;
            if ($node == null || $node == undefined) {
                $node = this.$el;
            }
            $tdList = $node.find('td.f_item_number');
            for (let td of $tdList) {
                $(td).html('<strong>' + index.toString() + '</strong>');
                index++;
            }
        },
        _renderBody: function () {
            let $tbody = this._super(...arguments);
            this._compute_line_no($tbody)
            return $tbody;

        },
        _renderRow: function (record) {
            var $row = this._super(record);
            var self = this;
            if (self.mode !== 'edit' && self.state.groupedBy.length == 0) {
                var index = self.state.data.findIndex(function (e) {
                    return record.id === e.id
                })
                    if (index !==  - 1) {
                        let display_type = record.data.display_type;
                        if (display_type) {
                            if (['line_note', 'line_section'].some(x => x == display_type)) {
                                $row.prepend($('<td>').html());
                                return $row
                            }
                        }
                        $row.prepend($('<td class="f_item_number">'));
                        this.skip_count = 0;
                    }
            }
            return $row;
        },

        _renderFooter: function (isGrouped) {
            var $footer = this._super(isGrouped);
            $footer.find("tr").prepend($('<td class="f_item_blank">').html('&nbsp;'));
            return $footer;
        },

    });

});
