// PriceHunter API Client
const API = {
  async search(params) {
    const response = await fetch('/api/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Error en la petición' }));
      throw new Error(err.detail || 'Error al buscar competidores');
    }
    return response.json();
  },

  async getHistory() {
    const response = await fetch('/api/history');
    if (!response.ok) throw new Error('Error al cargar historial');
    return response.json();
  },

  async clearHistory() {
    const response = await fetch('/api/history', { method: 'DELETE' });
    if (!response.ok) throw new Error('Error al limpiar historial');
    return response.json();
  },

  async addManual(data) {
    const response = await fetch('/api/manual', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Error al registrar' }));
      throw new Error(err.detail || 'Error al guardar producto manual');
    }
    return response.json();
  },

  async exportCsv(products) {
    const response = await fetch('/api/export/csv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(products),
    });
    if (!response.ok) throw new Error('Error al generar CSV');
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `PriceHunter_Reporte_${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  },

  async getHealth() {
    const response = await fetch('/api/health');
    if (!response.ok) throw new Error('Error en healthcheck');
    return response.json();
  }
};
