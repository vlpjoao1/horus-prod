// Creamos una funcion para refrescar el datatable solo llamandolo
var tbClient;

function getData() {
    //Asignamos el datatable a una variable para poder acceder a sus metodos
    tbClient = $('#data').DataTable({
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
            dataSrc: ""
        },
        columns: [
            {"data": "id"},
            {"data": "names"},
            {"data": "surnames"},
            {"data": "dni"},
            {"data": "date_birthday"},
            {"data": "gender.name"},
            {"data": "id"},
        ],
        //definimos las columnas una por una, especificando su posicion
        columnDefs: [
            {
                targets: [-1],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    //Rel establece el tipo de relacion entre el vincunlo y el documento asociado
                    var buttons = '<a href="#" rel="edit" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-edit"></i></a> ';
                    buttons += '<a href="#" rel="delete" type="button" class="btn btn-danger btn-xs btn-flat"><i class="fas fa-trash-alt"></i></a>';
                    return buttons;
                }
            },
        ],
        //se ejecuta cuando ya se cargue la tabla
        initComplete: function (settings, json) {

        }
    });
};
$(function () {
    // Seleccionamos el titulo del modal para poder modificar lo que este dentro de el
    modal_title = $('.modal-title');

    getData();
    // Crear Cliente---------------------------
    $('.btnAdd').on('click', function () {
        // Agregamos el valor add ya que desde JS cambiaremos a editar
        $('input[name="action"]').val('add');

        //Modificamos el span del modal_header desde aqui
        modal_title.find('span').html(' Creacion de un cliente');
        modal_title.find('i').removeClass().addClass('fas fa-plus')

        //Se hace de esta forma por si hay varios formularios
        //$('form')[0].reset();
        $('#myModalClient').modal('show');
    });
    //End-Crear Cliente------------------------

    //Editar Cliente---------------------------
    $('#data tbody')
        .on('click', 'a[rel="edit"]', function () {
            modal_title.find('span').html(' Edicion de un cliente');
            modal_title.find('i').removeClass().addClass('fas fa-edit')
            /* tbClient es la tabla que ya inicializamos
            * le pasamos como parametro el row actual
            * parents obtiene el elemento padre del THIS que le pasemos
            * data obtiene la DATA de ese row
            * */
            //Obtenemos el padre si es un LI o un TD
            var tr = tbClient.cell($(this).closest('td, li')).index();
            // pasamos el row de ese TR y obtenemos la data
            var data = tbClient.row(tr.row).data();
            // set values on form-----------------------------
            $('input[name="action"]').val('edit');
            $('input[name="id"]').val(data.id);
            $('input[name="names"]').val(data.names);
            $('input[name="surnames"]').val(data.names);
            $('input[name="dni"]').val(data.names);
            $('input[name="date_birthday"]').val(data.names);
            $('input[name="addres"]').val(data.names);
            //Como en el gender tambien tiene la propiedad ID lo seleccionamos por su ID
            $('select[name="gender"]').val(data.gender.id);
            //abrimos el modal despues de setearle los datos.
            $('#myModalClient').modal('show');
        })
        /*Como estamos haciendo referencia a la misma tabla podemos
            concatenar las acciones, asi se ejecuta una o la otra.
        * */
        .on('click', 'a[rel="delete"]', function () {
            var tr = tbClient.cell($(this).closest('td, li')).index();
            var data = tbClient.row(tr.row).data();
            //Lo enviamos con ajax debido a que el EDIT tenia un formulario
            var parameters = new FormData();
            //pasamos el action y el id de lo que eliminaremos.
            parameters.append('action', 'delete');
            parameters.append('id', data.id);
            submit_with_ajax(window.location.pathname, 'Notificación', '¿Estás seguro de que deseas eliminar el siguiente registro?', parameters, function () {
                //Con esto podemos reload el ajax https://datatables.net/reference/api/ajax.reload()
                tbClient.ajax.reload();
            });
        });
    //End-Editar Cliente-----------------------

    //Cuando se oculte el modal ejecute esta funcion
    $('#myModalClient').on('shown.bs.modal', function () {
        //$('form')[0].reset();
    });

    $('form').on('submit', function (e) {
        e.preventDefault();
        //aquí hacemos referencia al formulario
        //Esto obtiene a forma de diccionario todos los datos del formulario
        //Serializa los datos obtenidos del formulario
        //var parameters = $(this).serializeArray();
        //El formdata incluye los archivos FILES, Le pasamos el formulario como argumento
        var parameters = new FormData(this);
        // new FormData($('form')[0]) -> Si tenemos varios formularios y queremos escoger 1
        //parameters.forEach((key,value)=>console.log(key+':'+value)); -> si queremos iterar cada valor
        submit_with_ajax(window.location.pathname, 'Notificación', '¿Estás seguro de que deseas realizar la siguiente acción?', parameters, function () {
            //ocultamos el modal
            $('#myModalClient').modal('hide');
            //refrescamos el datatable
            //getData(); -- Puede ser de esta forma o
            //Con esto podemos reload el ajax https://datatables.net/reference/api/ajax.reload()
            tbClient.ajax.reload();
        });
    });
});
