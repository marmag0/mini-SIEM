document.addEventListener('DOMContentLoaded', function() {
    loadHosts();
});

// 1. Download host list and populate table
async function loadHosts() {
    try {
        const response = await fetch('/api/hosts/');
        const hosts = await response.json();
        
        const tbody = document.querySelector('#hosts-table tbody');
        tbody.innerHTML = ''; // Clear existing rows
        
        document.getElementById('stats-hosts-count').innerText = hosts.length;

        hosts.forEach(host => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="fw-bold text-primary">${host.name}</td>
                <td>${host.ip}</td>
                <td><span class="badge bg-secondary">${host.os}</span></td>
                <td><span class="badge bg-dark border border-secondary">Unknown</span></td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="deleteHost(${host.id})">Usuń</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
        
        // Refresh last update time
        const now = new Date();
        document.getElementById('last-update').innerText = now.toLocaleTimeString();

    } catch (error) {
        console.error('Błąd pobierania hostów:', error);
    }
}

// Add host form submission
async function submitHost() {
    const name = document.getElementById('host-name').value;
    const ip = document.getElementById('host-ip').value;
    const os = document.getElementById('host-os').value;
    
    try {
        const response = await fetch('/api/hosts/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, ip, os })
        });

        if (response.ok) {
            // Close modal and refresh host list
            const modal = bootstrap.Modal.getInstance(document.getElementById('addHostModal'));
            modal.hide();
            loadHosts();
            document.getElementById('add-host-form').reset();
        } else {
            const err = await response.json();
            alert('Błąd: ' + err.error);
        }
    } catch (error) {
        console.error('Błąd zapisu:', error);
    }
}

// Delete host
async function deleteHost(id) {
    if(!confirm('Czy na pewno usunąć maszynę?')) return;

    try {
        const response = await fetch(`/api/hosts/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadHosts();
        }
    } catch (error) {
        console.error('Błąd usuwania:', error);
    }
}