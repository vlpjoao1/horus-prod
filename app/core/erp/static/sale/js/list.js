var tblSale;

//funcion renderizar tabla de detalle
function format(d) {
    console.log(d);
    var html = '<table class="table table-striped">';
    html += '<thead class="thead-dark">';
    //open tr
    html += '<tr> <th scope="col">Productos</th>';
    html += '<th scope="col">Categoria</th>';
    html += '<th scope="col">PVP</th>';
    html += '<th scope="col">Cantidad</th>';
    html += '<th scope="col">Subtotal</th></tr>';
    //close tr
    html += '</thead>';
    html += '<tbody>';
    // Se itera detalle ya que ahi es donde estan los detalles de la venta.
    $.each(d.det, function (key, value) {
        // Iteramos key:value ya que viene asi los datos (0:{id: 3, prod: {…}, price: '111.00', cant: 1, subtotal: '111.00'})
        html += '<tr>'
        html += '<td>' + value.prod.name + '</td>';
        html += '<td>' + value.prod.cat.name + '</td>';
        html += '<td>' + value.price + '</td>';
        html += '<td>' + value.cant + '</td>';
        html += '<td>' + value.subtotal + '</td>';
        html += '</tr>'
    });
    html += '</tbody>';
    return html;
}

//Codigo copiado de algorisoft, por ahorro de tiempo
$(function () {
    //Listado general de la tabla
    tblSale = $('#data').DataTable({
        //responsive: true, //Quitamos el responsive porque la tabla se cambia y no funciona el child_rows
        scrollX: true, //Activamos el scroll para que al ahcer chica la pantalla se muestre
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'searchdata'
            },
            dataSrc: ""
        },
        columns: [
            //{"data": "id"},
            //https://datatables.net/examples/api/row_details.html
            // Sustituimos el primer valor con una columna que editaremos para que tenga el +
            {
                className: 'dt-control',
                orderable: false,
                data: null,
                defaultContent: '',
            },
            {"data": "cli.names"},
            {"data": "date_joined"},
            {"data": "subtotal"},
            {"data": "iva"},
            {"data": "total"},
            {"data": "id"},
        ],
        columnDefs: [
            {
                targets: [-2, -3, -4],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return '$' + parseFloat(data).toFixed(2);
                }
            },
            {
                targets: [-1],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var buttons = '<a href="/erp/sale/delete/' + row.id + '/" class="btn btn-danger btn-xs btn-flat"><i class="fas fa-trash-alt"></i></a> ';
                    buttons += '<a href="/erp/sale/update/' + row.id + '/" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-edit"></i></a> ';
                    buttons += '<a rel="details" class="btn btn-success btn-xs btn-flat"><i class="fas fa-search"></i></a> ';
                    buttons += '<a href="/erp/sale/invoice/pdf/'+row.id+'/" target="_blank" class="btn btn-info btn-xs btn-flat"><i class="fas fa-file-pdf"></i></a> ';
                    return buttons;
                }
            },
        ],
        initComplete: function (settings, json) {

        }
    });

    // Obteniendo detalles de la venta. Es decir, los productos.
    $('#data tbody')
        //cuando presionamos el a de detalle, se ejecute lo siguiente
        .on('click', 'a[rel="details"]', function () {
            // obtenemos la posicion de la fila
            //Se hace de esta manera porque en responsive se crean los LI
            var tr = tblSale.cell($(this).closest('td, li')).index();
            // Obtenemos el objeto de la fila
            var data = tblSale.row(tr.row).data();
            console.log(data);

            // Cargamos los datos en la tabla del MODAL y a su vez hacemos la busqueda
            $('#tblDet').DataTable({
                responsive: true,
                autoWidth: false,
                destroy: true,
                deferRender: true,
                /*En el modelo creamos un valor llamado DET (item['det'] = [i.toJSON() for i in self.detsale_set.all()])
                Esto devuelve todos los productos(detalles) de esa venta y ya estarian cargados en la pagina, por lo que
                no habria que hacer una consulta AJAX, pero esto no es conveniente ya que pueden haber cambios en la DB
                * */ //https://youtu.be/UeGI2dhyZeI?list=PLxm9hnvxnn-j5ZDOgQS63UIBxQytPdCG7&t=808
                //data: data.det, //Esto traeria los datos almacenados en memoria y no en tiempo real.
                ajax: {
                    url: window.location.pathname,
                    type: 'POST',
                    //Enviamos los parametros de busqueda a la vista
                    data: {
                        'action': 'search_details_prod',
                        'id': data.id
                    },
                    dataSrc: ""
                },
                columns: [
                    // Definimos que dato tendra asociado cada columna
                    {"data": "prod.name"},
                    {"data": "prod.cat.name"},
                    {"data": "price"},
                    {"data": "cant"},
                    {"data": "subtotal"},
                ],
                columnDefs: [
                    {
                        //price / subtotal
                        targets: [-1, -3],
                        class: 'text-center',
                        render: function (data, type, row) {
                            return '$' + parseFloat(data).toFixed(2);
                        }
                    },
                    {
                        //cant
                        targets: [-2],
                        class: 'text-center',
                        render: function (data, type, row) {
                            return data;
                        }
                    },
                ],
                initComplete: function (settings, json) {

                }
            });
            $('#myModalDet').modal('show');
        })
        //Detalles pero con child_rows
        .on('click', 'td.dt-control', function () {
            //Aqui lo hacemos de esta manera porque el responsive no se usa, y no se crean los LI
            var tr = $(this).closest('tr');
            var row = tblSale.row(tr);
            //Si esta abierto el componente lo oculta, sino lo abrira
            if (row.child.isShown()) {
                // This row is already open - close it
                row.child.hide();
                tr.removeClass('shown');
            } else {
                // Open this row
                /*
                row.data()= extrae la informacion de la fila.
                format()= Funcion que crea el html y le pasas la data
                * */
                row.child(format(row.data())).show();
                tr.addClass('shown');
            }
        });
    ;
});