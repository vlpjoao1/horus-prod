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
                'action': 'searchdata'
            },//parameters
            //dataSrc se usa para especificar una key dentro de un dict. https://datatables.net/manual/ajax#JSON-data-source
            dataSrc: ''
        },
        columns: [
            {'data': 'id'},
            {'data': 'full_name'},
            {'data': 'username'},
            {'data': 'date_joined'},
            {'data': 'image'},
            {'data': 'groups'},
            //Para las opciones, igual lo definimos
            {'data': 'id'}
        ],
        //definimos las columnas una por una, especificando su posicion
        columnDefs: [
            {
                targets: [-3],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    // puede ser data / row.image, cualquiera de los dos
                    return '<img src="' + row.image + '" class="img-fluid mx-auto d-block" style="width: 20px; height: 20px;">';
                }
            },
            {
                targets: [-2],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var html = '';
                    /* Renderizamos la lista de arrays en la columna */
                    $.each(row.groups, function (key, value) {
                        html += '<span class="badge badge-success">' + value.name + '</span> ';
                    });
                    return html;
                }
            },
            {
                targets: [-1],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var buttons = '<a href="/user/update/' + row.id + '/" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-edit"></i></a>';
                    buttons += ' <a href="/user/delete/' + row.id + '/" type="button" class="btn btn-danger btn-xs btn-flat"><i class="fas fa-trash-alt"></i></a>';
                    return buttons;
                }
            },
        ],
        //se ejecuta cuando ya se cargue la tabla
        initComplete: function (settings, jsong) {
        }
    });
});