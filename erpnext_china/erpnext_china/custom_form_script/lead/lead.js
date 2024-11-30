// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
// Script for ToDo Form
frappe.ui.form.on('Lead', {
    // on refresh event
    refresh(frm) {
        frm.set_query('source', () => {
            return {
                query: 'erpnext_china.erpnext_china.custom_form_script.lead_source.lead_source.custom_source_query',
            }
        });
        frm.set_query('custom_product_category', () => {
            return {
                query: 'erpnext_china.erpnext_china.doctype.product_category.product_category.custom_product_category_query'
            }
        })
        if (!frm.is_new()) {

            const contactFields = ['phone', 'mobile_no', 'custom_wechat']
            // 如果不是网络推广管理和管理员，其它人都不能编辑联系方式
            const readOnly = !frappe.user.has_role('网络推广管理') && !frappe.user.has_role('System Manager')
            if (readOnly) {
                contactFields.forEach(field => {
                    frm.fields_dict[field].df.read_only = !!frm.doc[field];
                });
            }

            // 如果是网络推广或者网推管理或者管理员或者是私海，则显示联系方式
            const show = frappe.user.has_role('网络推广') ||
                frappe.user.has_role('网络推广管理') ||
                frappe.user.has_role('System Manager') ||
                frm.doc.custom_sea == "私海";

            // 如果当前线索已经创建了客户，则线索负责员工不能再编辑
            if (frm.doc.__onload.is_customer && !frappe.user.has_role('System Manager') && !frappe.user.has_role('网络推广管理')) {
                frm.fields_dict["custom_lead_owner_employee"].df.read_only = 1;
                frm.refresh_field("custom_lead_owner_employee");
            }

            contactFields.forEach(field => {
                frm.fields_dict[field].df.hidden = !show; // 隐藏联系方式
                frm.refresh_field(field);
            });

            if (!show) {
                // 提示认领
                frm.set_intro();
                frm.set_intro(__("请在右上角【行动】或【...】中点击【认领线索】查看联系方式。"));
            }

            // 如果不是管理员，则隐藏 notes子表
            if (!frappe.user.has_role('System Manager')) {
                frm.set_df_property("notes", "hidden", "1")
            }

            // 如果当前用户是线索负责人并且当前线索没有创建客户可以放弃线索
            if (frappe.session.user == frm.doc.lead_owner && !frm.doc.__onload.is_customer) {
                frm.add_custom_button(__("放弃线索"), () => {
                    let d = new frappe.ui.Dialog({
                        title: '请填写放弃原因',
                        fields: [
                            {
                                label: '反馈内容',
                                fieldname: 'content',
                                fieldtype: 'Text',
                                reqd: '1'
                            }
                        ],
                        size: 'small',
                        primary_action_label: '确定',
                        primary_action(values) {
                            let content = values['content'];
                            content = content.trim()
                            if (content.length < 3) {
                                frappe.throw("内容必须大于3个字！")
                            }
                            const firstChar = content[0];
                            let isDieci = true;
                            for (let i = 1; i < content.length; i++) {
                                if (content[i] !== firstChar) {
                                    isDieci = false
                                    break
                                }
                            }
                            if (isDieci) {
                                frappe.throw("内容格式错误！")
                            }
                            frappe.call("erpnext_china.erpnext_china.custom_form_script.lead.lead.give_up_lead", {
                                lead: frm.doc.name,
                                content: "放弃原因：" + content
                            }).then((r) => {
                                if (r && r.message == 200) {
                                    window.location.reload();
                                }
                            })
                            d.hide();
                        }
                    });

                    d.show();

                }, __("Action"));
            } else {
                if (frm.doc.lead_owner == "" || frm.doc.custom_sea == "公海") {
                    frm.add_custom_button(__("认领线索"), () => {
                        // frappe.db.set_value('Lead', frm.doc.name, {lead_owner: frappe.session.user});
                        frappe.call("erpnext_china.erpnext_china.custom_form_script.lead.lead.get_lead", { lead: frm.doc.name }).then((r) => {
                            if (r && r.message == 200) {
                                window.location.reload();
                            }
                        })

                    }, __("Action"));
                }
            }
            
            // 展示是否已经查看过
            if (frm.meta.track_views && frm.doc.lead_owner) {
                frappe.call("erpnext_china.erpnext_china.custom_form_script.lead.lead.get_viewed_on",
                    {
                        lead: frm.doc.name,
                        lead_owner: frm.doc.lead_owner
                    }).then((r) => {
                        if (r.message && r.message.viewed_on) {
                            const viewedOn = r.message.viewed_on;
                            const viewedDom = $(`<li style="margin-bottom: var(--margin-md);">
                        <span>${frm.doc.custom_lead_owner_name} 已经查看</span>
                        <span class="frappe-timestamp " data-timestamp="${viewedOn}" title="${viewedOn}">${comment_when(viewedOn)}</span>
                        </li>`)
                            viewedDom.insertBefore(frm.page.sidebar.find('.modified-by'));
                        }
                    })
            }

        }

        frappe.db.get_value('User', filters={'name': frappe.user.name, 'role_profile_name': '网推'}, fieldname='name').then(r=>{
            console.log(r)
            if (r.message.name) {
                frm.set_df_property("source", "reqd", "1");
                frm.refresh_field("source");
            }
            if((!r.message.name || !frm.doc.custom_auto_allocation) && frm.is_new()) {
                frm.doc.source = '其它'
                frm.doc.custom_other_source = '业务自录入'
                frm.refresh_field("source");
            }
        })
    },

})