function registrarHoras() {
    const data = document.getElementById('data').value;

    // Pegando os horários da manhã
    const horarioInicioManha = document.getElementById('horario-inicio-manha').value;
    const horarioFimManha = document.getElementById('horario-fim-manha').value;

    // Pegando os horários da noite
    const horarioInicioNoite = document.getElementById('horario-inicio-noite').value;
    const horarioFimNoite = document.getElementById('horario-fim-noite').value;

    let horarios = [];

    // Adicionar horário da manhã se for preenchido
    if (horarioInicioManha && horarioFimManha) {
        horarios.push(`Manhã: ${horarioInicioManha} - ${horarioFimManha}`);
    }

    // Adicionar horário da noite se for preenchido
    if (horarioInicioNoite && horarioFimNoite) {
        horarios.push(`Noite: ${horarioInicioNoite} - ${horarioFimNoite}`);
    }

    if (horarios.length === 0) {
        alert('Por favor, insira pelo menos um intervalo de horário.');
        return;
    }

    // Enviar dados ao servidor
    fetch('/registrar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            data: data,
            horarios: horarios
        }),
    })
    .then(response => response.json())
    .then(responseData => {
        alert(responseData.status);
        // Exibir os horários cadastrados no submenu, passando a data diretamente
        mostrarHorasCadastradas(data, horarios);
    })
    .catch((error) => {
        console.error('Erro:', error);
    });
}

function mostrarHorasCadastradas(data, horarios) {
    const listaHoras = document.getElementById('lista-horas');
    const submenu = document.getElementById('submenu-horas');

    // Garantir que o submenu esteja visível
    submenu.style.display = 'block';

    // Criar novo item de lista para a data e horários
    const listItem = document.createElement('li');
    listItem.innerText = `Data: ${data} - ${horarios.join(', ')}`;
    
    // Adicionar à lista
    listaHoras.appendChild(listItem);
}

function baixarRelatorio() {
    window.location.href = '/relatorio';
}
