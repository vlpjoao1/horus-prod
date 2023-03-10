//https://docs.djangoproject.com/en/3.2/ref/csrf/
/*Esto se usara para obtener el csrf del sitio y poder enviarlo a las vistas
* se usara para enviar el csrf a traves de ajax*/
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function message_error(obj, title = 'Error', icon = 'error') {
    //pasamos el objeto, y lo iteremos con each,
    //como es un diccionario usaremos una funcion y le pasaremos la clave y valor
    var html = '';
    if (typeof (obj) === 'object') {
        html += '<ul style="text-align: left;">';
        $.each(obj, function (key, value) {
            html += "<li>" + key + ': ' + value + '</li>';
        });
    } else {
        //De esta forma verificaría si el error es un objeto, ejemplo json, o si es otro tipo de error
        //lo enviaría a este else
        html += '<p>' + obj + '</p>';
    }
    html += '</ul>';
    Swal.fire({
        title: title,
        html: html,
        icon: icon
    });
};

//https://craftpip.github.io/jquery-confirm/
function submit_with_ajax(url, title, content, parameters, callback) {
    $.confirm({
        theme: 'material',
        title: title,
        icon: 'fa fa-info',
        content: content,
        columnClass: 'small',
        typeAnimated: true,
        cancelButtonClass: 'btn-primary',
        draggable: true,
        dragWindowBorder: false,
        buttons: {
            info: {
                text: "Si",
                btnClass: 'btn-primary',
                action: function () {
                    $.ajax({
                        url: url, //window.location.pathname
                        type: 'POST',
                        data: parameters,
                        // Pasamos el csrftoken por ajax para la vista
                        headers: {'X-CSRFToken': csrftoken},
                        dataType: 'json',
                        /* Esto se agrega al momento de enviar FILES en el formulario */
                        //Para que los datos enviados se transformen en un string
                        processData: false,
                        //Que no configure el tipo de dato recibido del servidor
                        contentType: false,
                    }).done(function (data) {
                        console.log(data, 'Functions.js');
                        if (!data.hasOwnProperty('error')) {
                            // Le enviamos los datos del ajax a la funcion para poder obtener el ID
                            callback(data);
                            return false;
                        }
                        message_error(data.error);
                    }).fail(function (jqXHR, textStatus, errorThrown) {
                        alert(textStatus + ': ' + errorThrown);
                    }).always(function (data) {

                    });
                }
            },
            danger: {
                text: "No",
                btnClass: 'btn-red',
                action: function () {

                }
            },
        }
    })
};

// Funcion para confirmar una accion
function alert_action(title, content, callback, cancel) {
    $.confirm({
        theme: 'material',
        title: title,
        icon: 'fa fa-info',
        content: content,
        columnClass: 'small',
        typeAnimated: true,
        cancelButtonClass: 'btn-primary',
        draggable: true,
        dragWindowBorder: false,
        buttons: {
            info: {
                text: "Si",
                btnClass: 'btn-primary',
                action: function () {
                    callback();
                }
            },
            danger: {
                text: "No",
                btnClass: 'btn-red',
                action: function () {
                    cancel();
                }
            },
        }
    })
};