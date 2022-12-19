var date_range = null;
var date_now = new moment().format('YYYY-MM-DD');

function generate_report(start_date, end_date) {
    var parameters = {
        'action': 'search_report',
        'start_date': date_now,
        'end_date': date_now
    }
    // Si la variable no es nula va a setear startdate y enddate  https://www.daterangepicker.com/#options
    if (date_range !== null) {
        parameters['start_date'] = date_range.startDate.format('YYYY-MM-DD');
        parameters['end_date'] = date_range.endDate.format('YYYY-MM-DD');
    }
    ;
    $('#data').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: parameters,
            dataSrc: ""
        },
        order: false,
        //Para quitarle algunas opciones de la pantalla del datatable
        paging: false,
        ordering: false,
        info: false,
        searching: false,
        // Para agregar los botonnes https://datatables.net/extensions/buttons/examples/initialisation/simple.html
        dom: 'Bfrtip',
        // Con esto definimos las caracteristicas que tendra cada boton
        buttons: [
            {
                extend: 'excelHtml5',
                text: 'Descargar Excel <i class="fas fa-file-excel"></i>',
                titleAttr: 'Excel',
                className: 'btn btn-success btn-flat btn-xs'
            },
            //Aqui definimos el formato que tendra el pdf y la apariencia del boton
            {
                extend: 'pdfHtml5',
                text: 'Descargar Pdf <i class="fas fa-file-pdf"></i>',
                titleAttr: 'PDF',
                className: 'btn btn-danger btn-flat btn-xs',
                download: 'open',
                orientation: 'landscape',
                pageSize: 'LEGAL',
                customize: function (doc) {
                    doc.styles = {
                        header: {
                            fontSize: 18,
                            bold: true,
                            alignment: 'center'
                        },
                        subheader: {
                            fontSize: 13,
                            bold: true
                        },
                        quote: {
                            italics: true
                        },
                        small: {
                            fontSize: 8
                        },
                        tableHeader: {
                            bold: true,
                            fontSize: 11,
                            color: 'white',
                            fillColor: '#2d4154',
                            alignment: 'center'
                        }
                    };
                    doc.content[1].table.widths = ['20%', '20%', '15%', '15%', '15%', '15%'];
                    doc.content[1].margin = [0, 35, 0, 0];
                    doc.content[1].layout = {};
                    doc['footer'] = (function (page, pages) {
                        return {
                            columns: [
                                {
                                    alignment: 'left',
                                    text: ['Fecha de creación: ', {text: date_now}]
                                },
                                {
                                    alignment: 'right',
                                    text: ['página ', {text: page.toString()}, ' de ', {text: pages.toString()}]
                                }
                            ],
                            margin: 20
                        }
                    });

                }
            }
        ],
        /*Cuando mandamos una lista desde python como se hace esta, noo hace falta definir las columnas desde aca
        * */
        // columns: [
        //     {"data": "id"},
        //     {"data": "name"},
        //     {"data": "cat.name"},
        //     {"data": "image"},
        //     {"data": "pvp"},
        //     {"data": "id"},
        // ],
        columnDefs: [
            {
                //Para el iva, total y subtotal
                targets: [-1, -2, -3],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return '$' + parseFloat(data).toFixed(2);
                }
            },
        ],
        initComplete: function (settings, json) {

        }
    });
};
$(function () {
    $('input[name="date_ranger"]').daterangepicker(
        {
            locale: {
                format: 'YYYY-MM-DD',
                applyLabel: '<i class="fas fa-chart-pie"></i> Aplicar',
                cancelLabel: '<i class="fas fa-times"></i> Cancelar',
            }
        }
    ).on('apply.daterangepicker', function (ev, picker) {
        //Picker contiene las fechas
        // var start_date = picker.startDate.format('YYYY-MM-DD');
        // var end_date = picker.endDate.format('YYYY-MM-DD');
        // generate_report(start_date,end_date);

        date_range = picker;
        generate_report();
    }).on('cancel.daterangepicker', function (ev, picker) {
        //Setea la fecha cuando damos en CANCELAR
        $(this).data('daterangepicker').setStartDate(date_now);
        $(this).data('daterangepicker').setEndDate(date_now);
        date_range = picker;
        generate_report();
    });
    generate_report();
});