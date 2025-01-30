
// Manejar la búsqueda y mostrar resultados
function manejarBusqueda() {
    document.getElementById('fetch-tickets').addEventListener('submit', function(e) {
        e.preventDefault();
        const nombre = document.getElementById('created_at').value;

        const cod_vend = document.getElementById('cod_vend').value;

        fetch('/tickets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nombre: nombre , cod_vend: cod_vend}),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return response.json();
        })
        .then(data => {
            actualizarResultados(data);
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('id01').innerText = 'Error procesando la solicitud.';
        });
    });
}
// Actualizar los resultados en la página
function actualizarResultados(data) {
    const resultadosDiv = document.getElementById('resultados2');
    resultadosDiv.innerHTML= '';

    if (data.resultados && data.resultados.length > 0) {
        const ul = document.createElement('ul');
        ul.classList.add('list-group');

        data.resultados.forEach(resultado => {
            const li = document.createElement('li');
            li.classList.add('list-group-item', 'mb-2');

            const mnt_ov = parseInt(resultado.MontoTotalOV, 10).toLocaleString('es-ES');
            const mnt_fac = parseInt(resultado.MontoTotalFA, 10).toLocaleString('es-ES');

            let fecha = new Date(resultado.Fecha);
            let fecha_formateada = fecha.toLocaleDateString('es-ES', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
            /*li.innerHTML = `
                <strong>${resultado.Nombre} (${resultado.Codigo})</strong>
                <br>Monto Pedido: ${mnt_ov}
                <br>Monto Factura: ${mnt_fac}
                <br>Nro Referencia: ${resultado.NroReferenciaFA}
                <br>Fecha: ${resultado.Fecha}
                <b><a href="/detalle_ovfa?vNroReferenciaOV=${encodeURIComponent(resultado.NroReferenciaOV)}" class="ver-detalle">Ver Comprobante</a></b>
                <b>
                        <a href="#" 
                           class="ver-detalle"
                           data-referencia="${resultado.NroReferenciaOV}" 
                           data-bs-toggle="modal" 
                           data-bs-target="#detalleModal">Ver Comprobante
                        </a>
                    </b>
            `;*/
            li.innerHTML = `
                <button class="collapsible" data-bs-toggle="collapse" data-bs-target="#collapse${resultado.NroReferenciaOV}">${resultado.Nombre} (${resultado.Codigo}) - ${resultado.NroReferenciaOV}</button>
                <div id="collapse${resultado.NroReferenciaOV}" class="collapse mt-2">
                    <b>Monto Pedido: ${mnt_ov}</b><br>
                    <b>Monto Factura: ${mnt_fac}</b><br>
                    <b>Nro Referencia: ${resultado.NroReferenciaOV}</b><br>
                    <b>Fecha Entrega: ${fecha_formateada}</b><br>
                    <b><a href="/detalle_ovfa?vNroReferenciaOV=${encodeURIComponent(resultado.NroReferenciaOV)}" class="ver-detalle">Ver Comprobante</a></b>
                </div>
            `;
            ul.appendChild(li);
        });   
        resultadosDiv.appendChild(ul);
    } else {
        resultadosDiv.innerText = '<p>No se encontraron resultados.</p>';
        resultadoUl.appendChild(li);
    }
}
// Manejar la edición de usuarios en el modal
function manejarEdicionUsuarios() {
    let editarUsuarioModal = document.getElementById('editarUsuarioModal');
    editarUsuarioModal.addEventListener('show.bs.modal', function (event) {
        let button = event.relatedTarget;
        let id = button.getAttribute('data-id');
        let nombre = button.getAttribute('data-nombre');
        let documento = button.getAttribute('data-documento');
        let password = button.getAttribute('data-password');     
        let form = editarUsuarioModal.querySelector('form');
        form.action = `/usuarios/editar/${id}`;
        form.querySelector('#editarUsuarioId').value = id;
        form.querySelector('#editarNombre').value = nombre;
        form.querySelector('#editarDocumento').value = documento;
        form.querySelector('#editarPassword').value = password;
    });
}
// Inicializar funciones al cargar el DOM
document.addEventListener('DOMContentLoaded', function() {
    manejarBusqueda();
   // manejarEdicionUsuarios();

    // Agregar evento para cargar detalles en el modal
  document.getElementById('resultados2').addEventListener('click', function (e) {
    if (e.target.tagName === 'A' && e.target.classList.contains('ver-detalle')) {
      e.preventDefault();
      const url = e.target.getAttribute('href');
      
      fetch(url)
        .then(response => response.text())
        .then(html => {
          document.getElementById('detalleModalBody').innerHTML = html;
          const modal = new bootstrap.Modal(document.getElementById('detalleModal'));
          modal.show();
        })
        .catch(error => {
          console.error('Error al cargar los detalles:', error);
          document.getElementById('detalleModalBody').innerHTML = '<p>Error al cargar los detalles.</p>';
        });
    }
  });

});
