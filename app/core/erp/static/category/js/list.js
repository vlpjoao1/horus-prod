$(function () {
    $('#data').dataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        //si cargamos la tabla con ajax, esto servirá como un async
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action':'searchdata'
            },//parameters
            //dataSrc se usa para especificar una key dentro de un dict. https://datatables.net/manual/ajax#JSON-data-source
            dataSrc: ''
        },
        columns: [
            {'data': 'position'},
            {'data': 'name'},
            {'data': 'desc'},
            {'data': 'desc'}
        ],
        //definimos las columnas una por una, especificando su posicion
        columnDefs: [
            {
                targets: [-1],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var buttons='<a href="/erp/category/update/' + row.id + '/" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-edit"></i></a>';
                    buttons +=' <a href="/erp/category/delete/' + row.id + '/" type="button" class="btn btn-danger btn-xs btn-flat"><i class="fas fa-trash-alt"></i></a>';
                    return buttons;
                }
            },
        ],
        //se ejecuta cuando ya se cargue la tabla
        initComplete: function (settings, jsong) {
        }
    });
});