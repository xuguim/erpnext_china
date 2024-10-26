
frappe.listview_settings['Product Category'] = {
    onload(listview) {
        const results = document.getElementsByClassName("result");
        if (results.length == 1) {
            new Sortable(results[0], {
                draggable: ".list-row-container",
                preventOnFilter: true,
                onUpdate: () => {
                    this.update_row_index();
                },
            });
        }
    },
    update_row_index() {
        const eles = document.querySelectorAll('.list-row-checkbox')
        const names = []
        eles.forEach((ele, index)=>{
            names.push({name: ele.dataset['name'], index: index})
        })
        
        frappe.call('erpnext_china.erpnext_china.doctype.product_category.product_category.update_sorted_index', {
            sorted: names
           }).then(r => {
               this.reload();
           })
    },
    reload() {
        const reloadBtn = document.querySelector("button[data-original-title='Reload List']");
        if (reloadBtn) {
            reloadBtn.click();
        }
    }
}