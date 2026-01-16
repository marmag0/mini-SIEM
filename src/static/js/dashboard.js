let alertsChart = null;

document.addEventListener('DOMContentLoaded', function() {
    loadHosts();
    loadAlerts();
    loadStats();
});

// Download host list and populate table
async function loadHosts() {
    try {
        const response = await fetch('/api/hosts/');
        const hosts = await response.json();
        const tbody = document.querySelector('#hosts-table tbody');
        tbody.innerHTML = '';
        
        document.getElementById('stats-hosts-count').innerText = hosts.length;

        hosts.forEach(host => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="fw-bold text-primary">${host.name}</td>
                <td>${host.ip}</td>
                <td><span class="badge bg-secondary">${host.os}</span></td>
                <td><span class="badge bg-success">Online</span></td>
                <td>
                    <div class="btn-group">
                        <button class="btn btn-outline-success btn-sm" onclick="fetchLogs(${host.id}, this)">📥 Scan</button>
                        <button class="btn btn-outline-danger btn-sm" onclick="deleteHost(${host.id})">🗑️</button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
        document.getElementById('last-update').innerText = new Date().toLocaleTimeString();
    } catch (e) { console.error('Błąd hostów:', e); }
}

// Download recent alerts and populate table
async function loadAlerts() {
    try {
        const response = await fetch('/api/alerts/recent');
        const alerts = await response.json();
        const tbody = document.querySelector('#alerts-table tbody');
        tbody.innerHTML = '';

        alerts.forEach(alert => {
            let badgeClass = 'bg-info';
            if (alert.severity === 'CRITICAL') badgeClass = 'bg-danger';
            if (alert.severity === 'WARNING') badgeClass = 'bg-warning text-dark';

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="text-secondary">${alert.timestamp}</td>
                <td><span class="badge ${badgeClass}">${alert.severity}</span></td>
                <td class="text-info">${alert.host}</td>
                <td>${alert.message}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) { console.error('Błąd alertów:', e); }
}

// Download alert stats and render chart
async function loadStats() {
    try {
        const response = await fetch('/api/alerts/stats');
        const stats = await response.json();

        // Counter update
        const criticalCount = stats['CRITICAL'] || 0;
        document.getElementById('stats-alerts-critical').innerText = criticalCount;

        const ctx = document.getElementById('alertsChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (alertsChart) alertsChart.destroy();

        alertsChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Critical', 'Warning', 'Info'],
                datasets: [{
                    data: [stats['CRITICAL'] || 0, stats['WARNING'] || 0, stats['INFO'] || 0],
                    backgroundColor: ['#dc3545', '#ffc107', '#0dcaf0'],
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#fff' } }
                }
            }
        });
    } catch (e) { console.error('Błąd statystyk:', e); }
}

// Fetch logs for a host
async function fetchLogs(id, btn) {
    const originalText = btn.innerHTML;
    btn.innerHTML = '⏳ Skanuję...';
    btn.disabled = true;

    try {
        const response = await fetch(`/api/hosts/${id}/fetch`, { method: 'POST' });
        const data = await response.json();

        if (response.ok) {
            loadAlerts();
            loadStats();
            
            if (data.alerts_generated > 0) {
                alert(`⚠️ WYKRYTO ZAGROŻENIA!\nNowe krytyczne alerty: ${data.alerts_generated}`);
            } else {
                alert(`✅ Skanowanie zakończone. Brak nowych zagrożeń krytycznych.`);
            }
        } else {
            alert('Błąd: ' + (data.message || data.error));
        }
    } catch (e) { console.error('Error:', e); }
    finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Submit new host form
async function submitHost() {
    const name = document.getElementById('host-name').value;
    const ip = document.getElementById('host-ip').value;
    const os = document.getElementById('host-os').value;
    try {
        const response = await fetch('/api/hosts/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, ip, os })
        });
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('addHostModal')).hide();
            loadHosts();
            document.getElementById('add-host-form').reset();
        }
    } catch (e) { console.error(e); }
}

async function deleteHost(id) {
    if(!confirm('Usunąć maszynę?')) return;
    try {
        const response = await fetch(`/api/hosts/${id}`, { method: 'DELETE' });
        if (response.ok) loadHosts();
    } catch (e) { console.error(e); }
}

async function loadIpThreats() {
    try {
        const response = await fetch('/api/alerts/ip-stats');
        const threats = await response.json();
        const tbody = document.querySelector('#threats-table tbody');
        tbody.innerHTML = '';

        if (threats.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Brak powtarzających się ataków.</td></tr>';
            return;
        }

        threats.forEach(t => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="fw-bold text-warning">${t.ip}</td>
                <td><span class="badge bg-secondary">${t.count}</span></td>
                <td><span class="badge ${t.severity === 'CRITICAL' ? 'bg-danger' : 'bg-warning text-dark'}">${t.severity}</span></td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="blockIp(1, '${t.ip}', this)">
                        🚫 Zablokuj IP
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) { console.error('Błąd ładowania zagrożeń:', e); }
}

// Block IP on firewall
async function blockIp(hostId, ip, btn) {
    if (!confirm(`Czy na pewno zablokować IP ${ip} na firewallu?`)) return;
    
    const originalText = btn.innerHTML;
    btn.innerHTML = '⏳ Blokuję...';
    btn.disabled = true;

    try {
        const response = await fetch(`/api/hosts/${hostId}/block-ip`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ip: ip })
        });
        const data = await response.json();

        if (response.ok) {
            alert('Sukces: ' + data.message);
            loadIpThreats(); // Refresh the threats list
        } else {
            alert('Błąd: ' + data.error);
        }
    } catch (e) { console.error(e); }
    finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    loadIpThreats();
});