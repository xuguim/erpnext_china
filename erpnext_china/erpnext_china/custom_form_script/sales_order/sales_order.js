frappe.ui.form.on('Sales Order', {
	onload(frm) {
        
		// 销售订单选择物料时，只选择已经定义的UOM
		frm.fields_dict['items'].grid.get_field('uom').get_query = function(doc, cdt, cdn){
			var row = locals[cdt][cdn];
			return {
				query:"erpnext.accounts.doctype.pricing_rule.pricing_rule.get_item_uoms",
				filters: {'value':row.item_code, apply_on:"Item Code"},
			}
		};
	},
    refresh(frm){
        frm.call('get_p13').then((r)=>{
            const name = r.message.name;
            if (name) {
                frm.doc.taxes_and_charges = name
            }
        });
        // 设置子表字段的筛选条件
        frm.set_query("item_code", "items", function(doc) {
            return {
                filters: [
                    ["Item", "disabled", "=", 0], // 只显示启用的项目
                    ["Item", "has_variants", "=", 0], // 不显示变体项目
                    ["Item", "is_sales_item", "=", 1], // 只显示销售项目
                    ["Item", "item_group", "descendants of (inclusive)", "成品"] // 只显示成品组的项目
                    // ["Item", "company", "in", [doc.company]] // 匹配主表的公司字段
                ]
            };
        });

        // 添加按钮弹出dialog来筛选收付款凭证
        if(frappe.user.has_role('销售会计')) {
            frm.add_custom_button(
                __("查看收付款凭证"),
                () => frm.events.select_payment_entry(frm),
            );
        }
    },
    select_payment_entry(frm) {
        const handleFieldOnChange = ()=>{
            const query = {
                payment_type: dialog.get_value("payment_type"),
                company: dialog.get_value("company"),
                bank_account: dialog.get_value("bank_account"),
                party: dialog.get_value("party"),
                total_allocated_amount: dialog.get_value("total_allocated_amount"),
                unallocated_amount: dialog.get_value("unallocated_amount"),
                reference_no: dialog.get_value("reference_no"),
                reference_date: dialog.get_value("reference_date"),
                custom_payment_note: dialog.get_value("custom_payment_note"),
            }
            frappe.call("erpnext_china.erpnext_china.custom_form_script.sales_order.sales_order.select_payment_entry", query).then(r=>{
                dialog.fields_dict.items.df.data.length = 0;
                if (r.message && r.message.length > 0) {
                    r.message.forEach(pm => {
                        dialog.fields_dict.items.df.data.push({
                            name: pm.name,
                            bank_account: pm.bank_account,
                            total_allocated_amount: pm.total_allocated_amount,
                            unallocated_amount: pm.unallocated_amount,
                            reference_no: pm.reference_no,
                            reference_date: pm.reference_date,
                            custom_payment_note: pm.custom_payment_note
                        });
                    });
                }
                dialog.fields_dict.items.grid.refresh();
            })
        }
		const dialog = new frappe.ui.Dialog({
			title: __("查看收付款凭证"),
			size: "extra-large",
			fields: [
				{
					fieldname: "payment_type",
					fieldtype: "Select",
					label: __("收付款类型"),
					options: "Receive\nPay\nInternal Transfer",
					default: "Receive",
                    onchange: ()=>{
                        handleFieldOnChange()
                    }
				},
                {
					fieldname: "company",
					fieldtype: "Link",
					label: __("Company"),
					options: "Company",
					default: frm.doc.company,
                    onchange: ()=>{
                        handleFieldOnChange()
                    }
				},
                {
					fieldname: "bank_account",
					fieldtype: "Link",
					label: __("Bank Account"),
					options: "Bank Account",
                    get_query: () => {
						return {
							filters: [["Bank Account", "company", "=", dialog.get_value("company")]],
						};
					},
                    onchange: ()=>{
                        handleFieldOnChange()
                    }
				},
                {
					fieldname: "party",
					fieldtype: "Link",
					label: __("往来单位"),
					options: "Customer",
					default: frm.doc.customer,
                    onchange: ()=>{
                        handleFieldOnChange()
                    }
				},
				{ fieldtype: "Column Break" },
                {
					fieldname: "total_allocated_amount",
					fieldtype: "Data",
					label: __("已付金额(CNY)"),
                    onchange: ()=>{
                        handleFieldOnChange()
                    }
				},
                {
					fieldname: "unallocated_amount",
					fieldtype: "Data",
					label: __("未付金额(CNY)"),
                    default: frm.doc.total,
                    onchange: ()=>{
                        handleFieldOnChange()
                    }
				},
                {
					fieldname: "reference_no",
					fieldtype: "Data",
					label: __("参考编号"),
                    onchange: ()=>{
                        handleFieldOnChange()
                    }
				},
                {
					fieldname: "reference_date",
					fieldtype: "Date",
					label: __("参考日期"),
                    onchange: ()=>{
                        handleFieldOnChange()
                    }
				},
                {
					fieldname: "custom_payment_note",
					fieldtype: "Data",
					label: __("转账备注"),
                    onchange: ()=>{
                        handleFieldOnChange()
                    }
				},
				{ fieldtype: "Section Break" },
				{
					fieldname: "items",
					fieldtype: "Table",
					label: __("收付款凭证"),
					allow_bulk_edit: false,
					cannot_add_rows: true,
					cannot_delete_rows: true,
					data: [],
					fields: [
						{
							fieldname: "name",
							fieldtype: "Link",
							label: __("Payment Entry"),
							options: "Payment Entry",
							read_only: 1,
							in_list_view: 1,
                            columns: 2,
						},
                        {
                            fieldname: "bank_account",
                            fieldtype: "Link",
                            label: __("Bank Account"),
                            options: "Bank Account",
                            read_only: 1,
							in_list_view: 1,
                        },
                        {
                            fieldname: "total_allocated_amount",
                            fieldtype: "Currency",
                            label: __("已付金额"),
                            read_only: 1,
							in_list_view: 1,
                            columns: 1,
                        },
                        {
                            fieldname: "unallocated_amount",
                            fieldtype: "Currency",
                            label: __("未付金额"),
                            read_only: 1,
							in_list_view: 1,
                            columns: 1,
                        },
                        {
                            fieldname: "reference_no",
                            fieldtype: "Data",
                            label: __("参考编号"),
                            read_only: 1,
							in_list_view: 1,
                        },
                        {
                            fieldname: "reference_date",
                            fieldtype: "Date",
                            label: __("参考日期"),
                            read_only: 1,
							in_list_view: 1,
                            columns: 1,
                        },
                        {
                            fieldname: "custom_payment_note",
                            fieldtype: "Data",
                            label: __("转账备注"),
                            read_only: 1,
							in_list_view: 1,
                        },
					],
				},
			],
            primary_action_label: __("查询"),
			primary_action: () => {
                handleFieldOnChange();
                frappe.msgprint('查询完成')
			},
        });
		dialog.fields_dict.items.grid.refresh();
		dialog.show();
        handleFieldOnChange();
	},
})


frappe.ui.form.on("Sales Order Item", {
	item_code: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
        row.warehouse = ''
		if (frm.doc.delivery_date) {
			row.delivery_date = frm.doc.delivery_date;
			refresh_field("delivery_date", cdn, "items");
		} else {
			frm.script_manager.copy_from_first_row("items", row, ["delivery_date"]);
		}
        frappe.call("erpnext_china_mdm.mdm.custom_form_script.item.item.get_item_default_warehouse", {item_code: row.item_code, company: frm.doc.company}).then((r)=>{
            if(r.message) {
                row.warehouse = r.message;
                refresh_field("warehouse", cdn, "items");
            }
        })
	},
	delivery_date: function (frm, cdt, cdn) {
		if (!frm.doc.delivery_date) {
			erpnext.utils.copy_value_in_all_rows(frm.doc, cdt, cdn, "items", "delivery_date");
		}
	}
});