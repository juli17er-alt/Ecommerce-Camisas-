// PriceHunter Frontend Controller
document.addEventListener('DOMContentLoaded', () => {
  const state = {
    query: '',
    competitors: ['Undergold', 'Clement'],
    demoMode: false,
    loading: false,
    response: null,
    viewMode: 'cards', // 'cards' | 'table'
    sortBy: 'confidence', // 'confidence' | 'price_asc' | 'price_desc' | 'title'
    confidenceFilter: 'all',
    brandFilter: 'all',
    stockFilter: false,
    colorFilter: '',
    sizeFilter: '',
    minPrice: null,
    maxPrice: null,
  };

  // DOM Elements
  const searchForm = document.getElementById('search-form');
  const searchInput = document.getElementById('search-input');
  const searchBtn = document.getElementById('search-btn');
  const searchSpinner = document.getElementById('search-spinner');
  const searchBtnText = document.getElementById('search-btn-text');
  
  const checkUndergold = document.getElementById('check-undergold');
  const checkClement = document.getElementById('check-clement');
  const demoModeToggle = document.getElementById('demo-mode-toggle');
  const demoBanner = document.getElementById('demo-banner');
  
  const toggleFiltersBtn = document.getElementById('toggle-filters-btn');
  const advancedFiltersPanel = document.getElementById('advanced-filters-panel');
  const filterColor = document.getElementById('filter-color');
  const filterSize = document.getElementById('filter-size');
  const filterMinPrice = document.getElementById('filter-min-price');
  const filterMaxPrice = document.getElementById('filter-max-price');
  const filterStock = document.getElementById('filter-stock');
  const clearFiltersBtn = document.getElementById('clear-filters-btn');

  // Competitor Status Strip
  const statusStrip = document.getElementById('competitors-status-strip');
  
  // Summary Section
  const summarySection = document.getElementById('summary-section');
  const statLowestPrice = document.getElementById('stat-lowest-price');
  const statLowestProduct = document.getElementById('stat-lowest-product');
  const statHighestPrice = document.getElementById('stat-highest-price');
  const statHighestProduct = document.getElementById('stat-highest-product');
  const statAvgPrice = document.getElementById('stat-avg-price');
  const statPriceDiff = document.getElementById('stat-price-diff');
  const statTotalProds = document.getElementById('stat-total-prods');
  const verdictText = document.getElementById('verdict-text');
  const verdictBanner = document.getElementById('verdict-banner');

  // Results Section
  const resultsSection = document.getElementById('results-section');
  const resultsCount = document.getElementById('results-count');
  const freshnessTimestamp = document.getElementById('freshness-timestamp');
  const viewCardsBtn = document.getElementById('view-cards-btn');
  const viewTableBtn = document.getElementById('view-table-btn');
  const sortSelect = document.getElementById('sort-select');
  const brandFilterSelect = document.getElementById('brand-filter-select');
  const confidenceFilterSelect = document.getElementById('confidence-filter-select');
  const exportCsvBtn = document.getElementById('export-csv-btn');
  
  const cardsContainer = document.getElementById('cards-container');
  const tableContainer = document.getElementById('table-container');
  const productsTableBody = document.getElementById('products-table-body');
  const emptyState = document.getElementById('empty-state');
  const emptyMessage = document.getElementById('empty-message');

  // Modals
  const historyModal = document.getElementById('history-modal');
  const openHistoryBtn = document.getElementById('open-history-btn');
  const closeHistoryBtn = document.getElementById('close-history-btn');
  const historyList = document.getElementById('history-list');
  const clearHistoryBtn = document.getElementById('clear-history-btn');

  const manualModal = document.getElementById('manual-modal');
  const openManualBtn = document.getElementById('open-manual-btn');
  const closeManualBtn = document.getElementById('close-manual-btn');
  const manualForm = document.getElementById('manual-form');

  // Suggestions chips
  const suggestionChips = document.querySelectorAll('.suggestion-chip');

  // Currency Formatter
  function formatCOP(num) {
    if (num === null || num === undefined) return 'N/D';
    return '$ ' + Math.round(num).toLocaleString('es-CO') + ' COP';
  }

  // Format Date
  function formatDate(isoStr) {
    if (!isoStr) return '';
    try {
      const d = new Date(isoStr);
      return d.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' (' + d.toLocaleDateString('es-CO') + ')';
    } catch {
      return isoStr;
    }
  }

  // Update Competitor Selection
  function updateCompetitors() {
    state.competitors = [];
    if (checkUndergold.checked) state.competitors.push('Undergold');
    if (checkClement.checked) state.competitors.push('Clement');
  }

  // Toggle Advanced Filters
  toggleFiltersBtn.addEventListener('click', () => {
    advancedFiltersPanel.classList.toggle('hidden');
    const isHidden = advancedFiltersPanel.classList.contains('hidden');
    toggleFiltersBtn.innerHTML = isHidden 
      ? '<i data-lucide="sliders-horizontal" class="w-4 h-4 mr-1 inline"></i> Filtros avanzados'
      : '<i data-lucide="chevron-up" class="w-4 h-4 mr-1 inline"></i> Ocultar filtros';
    lucide.createIcons();
  });

  clearFiltersBtn.addEventListener('click', () => {
    filterColor.value = '';
    filterSize.value = '';
    filterMinPrice.value = '';
    filterMaxPrice.value = '';
    filterStock.checked = false;
    applyLocalFiltersAndRender();
  });

  // Suggestion Chips Click
  suggestionChips.forEach(chip => {
    chip.addEventListener('click', () => {
      searchInput.value = chip.getAttribute('data-query');
      searchForm.dispatchEvent(new Event('submit'));
    });
  });

  // Demo Mode Toggle
  demoModeToggle.addEventListener('change', (e) => {
    state.demoMode = e.target.checked;
    if (state.demoMode) {
      demoBanner.classList.remove('hidden');
    } else {
      demoBanner.classList.add('hidden');
    }
    // If there is an active search query, re-run with new demo mode
    if (searchInput.value.trim().length >= 2) {
      executeSearch();
    }
  });

  // Handle Search Submission
  searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    executeSearch();
  });

  async function executeSearch() {
    const q = searchInput.value.trim();
    if (q.length < 2) {
      alert('Por favor ingresa al menos 2 caracteres para buscar.');
      return;
    }

    updateCompetitors();
    if (state.competitors.length === 0) {
      alert('Debes seleccionar al menos una tienda competidora (Undergold o Clement).');
      return;
    }

    state.query = q;
    setLoading(true);

    const payload = {
      query: q,
      competitors: state.competitors,
      demo_mode: state.demoMode,
      category_filter: null,
      color_filter: filterColor.value.trim() || null,
      size_filter: filterSize.value.trim() || null,
      min_price: filterMinPrice.value ? parseFloat(filterMinPrice.value) : null,
      max_price: filterMaxPrice.value ? parseFloat(filterMaxPrice.value) : null,
      only_in_stock: filterStock.checked,
    };

    try {
      const data = await API.search(payload);
      state.response = data;
      renderAll(data);
    } catch (err) {
      console.error(err);
      alert(`Error en la búsqueda: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  function setLoading(isLoading) {
    state.loading = isLoading;
    if (isLoading) {
      searchBtn.disabled = true;
      searchSpinner.classList.remove('hidden');
      searchBtnText.textContent = 'Analizando competidores...';
    } else {
      searchBtn.disabled = false;
      searchSpinner.classList.add('hidden');
      searchBtnText.textContent = 'Buscar Competidores';
    }
  }

  // Render Full View
  function renderAll(data) {
    renderCompetitorsStatus(data.competitors_status);
    renderSummary(data.summary);
    renderResultsToolbar(data);
    applyLocalFiltersAndRender();
  }

  // Render Competitor Status Strip
  function renderCompetitorsStatus(statuses) {
    statusStrip.innerHTML = '';
    statuses.forEach(s => {
      let badgeClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      let icon = 'check-circle';
      let label = 'En Vivo';

      if (s.status === 'DEMO') {
        badgeClass = 'bg-blue-500/10 text-blue-400 border-blue-500/20';
        icon = 'info';
        label = 'Demostración';
      } else if (s.status === 'ERROR' || s.status === 'BLOCKED') {
        badgeClass = 'bg-rose-500/10 text-rose-400 border-rose-500/20';
        icon = 'alert-triangle';
        label = 'No disponible';
      } else if (s.status === 'EMPTY') {
        badgeClass = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
        icon = 'help-circle';
        label = 'Sin coincidencias';
      }

      const card = document.createElement('div');
      card.className = 'glass-card rounded-xl p-3 flex items-center justify-between';
      card.innerHTML = `
        <div class="flex items-center space-x-3">
          <div class="w-2.5 h-2.5 rounded-full ${s.status === 'OK' ? 'bg-emerald-400 animate-pulse' : (s.status === 'DEMO' ? 'bg-blue-400' : 'bg-rose-400')}"></div>
          <div>
            <div class="flex items-center space-x-2">
              <span class="font-semibold text-white text-sm">${s.name}</span>
              <span class="text-xs px-2 py-0.5 rounded-full border ${badgeClass} font-medium">${label}</span>
            </div>
            <p class="text-xs text-slate-400 mt-0.5">${s.message} • Latencia: ${s.response_time_ms}ms</p>
          </div>
        </div>
        <a href="${s.official_url}" target="_blank" rel="noopener noreferrer" class="text-xs text-slate-400 hover:text-emerald-400 flex items-center space-x-1 transition-colors">
          <span>Tienda</span>
          <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
        </a>
      `;
      statusStrip.appendChild(card);
    });
    lucide.createIcons();
  }

  // Render Summary Stats
  function renderSummary(summary) {
    if (!summary || summary.total_products === 0) {
      summarySection.classList.add('hidden');
      return;
    }
    summarySection.classList.remove('hidden');

    statLowestPrice.textContent = formatCOP(summary.lowest_price);
    statLowestProduct.textContent = `${summary.lowest_price_competitor}: ${summary.lowest_price_product || 'N/D'}`;

    statHighestPrice.textContent = formatCOP(summary.highest_price);
    statHighestProduct.textContent = `${summary.highest_price_competitor}: ${summary.highest_price_product || 'N/D'}`;

    statAvgPrice.textContent = formatCOP(summary.average_price);
    
    if (summary.is_comparable && summary.percentage_difference !== null) {
      statPriceDiff.textContent = `${summary.percentage_difference}% (${formatCOP(summary.absolute_difference)})`;
    } else {
      statPriceDiff.textContent = 'N/A (1 competidor)';
    }

    statTotalProds.textContent = `${summary.total_products} prendas`;

    verdictText.textContent = summary.comparison_verdict;
    if (summary.cheaper_competitor && summary.cheaper_competitor !== 'Empate') {
      verdictBanner.className = 'glass-card rounded-2xl p-5 border-l-4 border-l-emerald-500 bg-emerald-950/20';
    } else {
      verdictBanner.className = 'glass-card rounded-2xl p-5 border-l-4 border-l-violet-500 bg-violet-950/20';
    }
  }

  // Render Results Toolbar
  function renderResultsToolbar(data) {
    resultsSection.classList.remove('hidden');
    resultsCount.textContent = `${data.products.length} productos`;
    freshnessTimestamp.textContent = `Actualizado: ${formatDate(data.timestamp)}`;
  }

  // Filter & Sort Logic
  function getFilteredAndSortedProducts() {
    if (!state.response || !state.response.products) return [];
    let list = [...state.response.products];

    // Filter by Brand
    if (state.brandFilter !== 'all') {
      list = list.filter(p => p.competitor === state.brandFilter);
    }

    // Filter by Confidence
    if (state.confidenceFilter !== 'all') {
      list = list.filter(p => p.match_confidence === state.confidenceFilter);
    }

    // Sort
    if (state.sortBy === 'price_asc') {
      list.sort((a, b) => a.price_cop - b.price_cop);
    } else if (state.sortBy === 'price_desc') {
      list.sort((a, b) => b.price_cop - a.price_cop);
    } else if (state.sortBy === 'confidence') {
      list.sort((a, b) => b.similarity_score - a.similarity_score);
    } else if (state.sortBy === 'title') {
      list.sort((a, b) => a.title.localeCompare(b.title));
    }

    return list;
  }

  function applyLocalFiltersAndRender() {
    const prods = getFilteredAndSortedProducts();
    if (prods.length === 0) {
      cardsContainer.classList.add('hidden');
      tableContainer.classList.add('hidden');
      emptyState.classList.remove('hidden');
      emptyMessage.textContent = 'No hay productos que coincidan con los filtros aplicados.';
      return;
    }

    emptyState.classList.add('hidden');
    if (state.viewMode === 'cards') {
      cardsContainer.classList.remove('hidden');
      tableContainer.classList.add('hidden');
      renderCards(prods);
    } else {
      cardsContainer.classList.add('hidden');
      tableContainer.classList.remove('hidden');
      renderTable(prods);
    }
  }

  // Render Product Cards
  function renderCards(products) {
    cardsContainer.innerHTML = '';
    products.forEach(p => {
      const isLowest = p.price_rank === 1;
      const card = document.createElement('div');
      card.className = `glass-card rounded-2xl overflow-hidden flex flex-col justify-between ${isLowest ? 'rank-1-border' : ''}`;
      
      let badgeSourceClass = 'badge-live';
      let badgeSourceLabel = '🟢 En Vivo';
      if (p.data_source === 'DEMO') {
        badgeSourceClass = 'badge-demo';
        badgeSourceLabel = '🔵 Demo Data';
      } else if (p.data_source === 'MANUAL') {
        badgeSourceClass = 'badge-manual';
        badgeSourceLabel = '🟠 Manual';
      }

      let confBadgeClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      if (p.match_confidence === 'MEDIA') confBadgeClass = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      if (p.match_confidence === 'BAJA') confBadgeClass = 'bg-rose-500/10 text-rose-400 border-rose-500/20';

      const imgPlaceholder = `https://placehold.co/400x500/18181b/ffffff?text=${encodeURIComponent(p.title.slice(0, 20))}`;

      card.innerHTML = `
        <div>
          <!-- Image & Badges -->
          <div class="relative w-full h-64 bg-zinc-950 overflow-hidden group">
            <img 
              src="${p.image_url || imgPlaceholder}" 
              alt="${p.title}" 
              loading="lazy"
              class="w-full h-full object-cover object-top transition-transform duration-500 group-hover:scale-105"
              onerror="this.onerror=null;this.src='${imgPlaceholder}'"
            />
            <div class="absolute top-3 left-3 flex flex-col gap-1.5">
              <span class="text-xs px-2.5 py-1 rounded-full font-medium ${badgeSourceClass}">
                ${badgeSourceLabel}
              </span>
              ${isLowest ? '<span class="text-xs px-2.5 py-1 rounded-full font-bold bg-emerald-500 text-slate-950 shadow-md">#1 Más económico</span>' : ''}
            </div>
            <div class="absolute top-3 right-3">
              <span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-zinc-900/90 text-white border border-white/10 backdrop-blur-md">
                ${p.competitor}
              </span>
            </div>
            ${p.discount_pct ? `
              <div class="absolute bottom-3 right-3">
                <span class="text-xs font-bold px-2.5 py-1 rounded-full bg-rose-500 text-white shadow-lg">
                  -${p.discount_pct}% OFF
                </span>
              </div>
            ` : ''}
          </div>

          <!-- Body -->
          <div class="p-5">
            <!-- Confidence & Category -->
            <div class="flex items-center justify-between text-xs mb-2">
              <span class="text-slate-400">${p.category || 'Camisetas'}</span>
              <span class="px-2 py-0.5 rounded-full border font-medium ${confBadgeClass}" title="${p.match_explanation}">
                Coincidencia ${p.match_confidence} (${p.similarity_score}%)
              </span>
            </div>

            <!-- Title -->
            <h3 class="font-bold text-white text-base leading-snug line-clamp-2 hover:text-emerald-400 transition-colors" title="${p.title}">
              ${p.title}
            </h3>

            <!-- Explanation snippet -->
            <p class="text-xs text-slate-400 mt-2 line-clamp-2 italic" title="${p.match_explanation}">
              "${p.match_explanation}"
            </p>

            <!-- Attributes -->
            <div class="mt-4 flex flex-wrap gap-2 text-xs">
              <span class="px-2 py-1 rounded-md bg-zinc-800/80 text-slate-300 border border-white/5">
                Color: ${p.color || 'N/D'}
              </span>
              <span class="px-2 py-1 rounded-md ${p.available ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}">
                ${p.available ? 'En Stock' : 'Agotado'}
              </span>
            </div>

            <!-- Sizes -->
            ${p.sizes && p.sizes.length ? `
              <div class="mt-3 flex items-center space-x-1">
                <span class="text-xs text-slate-500 mr-1">Tallas:</span>
                <div class="flex flex-wrap gap-1">
                  ${p.sizes.slice(0, 5).map(sz => `<span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-900 text-slate-300 border border-zinc-700">${sz}</span>`).join('')}
                </div>
              </div>
            ` : ''}
          </div>
        </div>

        <!-- Footer / Price -->
        <div class="p-5 pt-0 border-t border-white/5 mt-4">
          <div class="flex items-baseline justify-between pt-3">
            <div>
              <span class="text-xs text-slate-400 block">Precio actual</span>
              <span class="text-xl font-extrabold text-white font-display tracking-tight">${formatCOP(p.price_cop)}</span>
              ${p.original_price_cop ? `<span class="text-xs text-slate-500 line-through ml-2">${formatCOP(p.original_price_cop)}</span>` : ''}
            </div>
            <a 
              href="${p.url}" 
              target="_blank" 
              rel="noopener noreferrer"
              class="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-emerald-500 text-slate-950 hover:bg-emerald-400 transition-all shadow-md active:scale-95"
            >
              <span>Ver en tienda</span>
              <i data-lucide="arrow-up-right" class="w-3.5 h-3.5"></i>
            </a>
          </div>
        </div>
      `;
      cardsContainer.appendChild(card);
    });
    lucide.createIcons();
  }

  // Render Product Table
  function renderTable(products) {
    productsTableBody.innerHTML = '';
    products.forEach(p => {
      const isLowest = p.price_rank === 1;
      const tr = document.createElement('tr');
      tr.className = `border-b border-white/5 hover:bg-white/[0.02] transition-colors ${isLowest ? 'bg-emerald-500/[0.04]' : ''}`;
      
      let badgeSourceClass = 'badge-live';
      let badgeSourceLabel = 'En Vivo';
      if (p.data_source === 'DEMO') {
        badgeSourceClass = 'badge-demo';
        badgeSourceLabel = 'Demo';
      } else if (p.data_source === 'MANUAL') {
        badgeSourceClass = 'badge-manual';
        badgeSourceLabel = 'Manual';
      }

      let confBadgeClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      if (p.match_confidence === 'MEDIA') confBadgeClass = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      if (p.match_confidence === 'BAJA') confBadgeClass = 'bg-rose-500/10 text-rose-400 border-rose-500/20';

      tr.innerHTML = `
        <td class="py-4 px-4 font-mono font-bold text-center ${isLowest ? 'text-emerald-400' : 'text-slate-400'}">
          #${p.price_rank || '-'}
        </td>
        <td class="py-4 px-4">
          <div class="flex items-center space-x-3">
            <div class="w-12 h-14 bg-zinc-900 rounded-lg overflow-hidden flex-shrink-0">
              <img src="${p.image_url || 'https://placehold.co/100x120/18181b/ffffff?text=Camiseta'}" alt="${p.title}" class="w-full h-full object-cover">
            </div>
            <div>
              <p class="font-bold text-white text-sm line-clamp-1">${p.title}</p>
              <div class="flex items-center space-x-2 text-xs text-slate-400 mt-0.5">
                <span>Color: ${p.color || 'N/D'}</span>
                <span>•</span>
                <span>Tallas: ${p.sizes.slice(0, 4).join(', ') || 'N/D'}</span>
              </div>
            </div>
          </div>
        </td>
        <td class="py-4 px-4 font-semibold text-slate-200">
          <span class="px-2.5 py-1 rounded-md bg-zinc-900 border border-white/5 text-xs">
            ${p.competitor}
          </span>
        </td>
        <td class="py-4 px-4">
          <span class="font-extrabold text-white font-display text-sm block">${formatCOP(p.price_cop)}</span>
          ${p.discount_pct ? `<span class="text-[10px] text-rose-400 font-bold">-${p.discount_pct}% OFF</span>` : ''}
        </td>
        <td class="py-4 px-4 text-slate-400 text-xs">
          ${p.original_price_cop ? `<span class="line-through">${formatCOP(p.original_price_cop)}</span>` : '-'}
        </td>
        <td class="py-4 px-4">
          <span class="text-xs px-2 py-0.5 rounded-full ${p.available ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}">
            ${p.available ? 'En Stock' : 'Agotado'}
          </span>
        </td>
        <td class="py-4 px-4">
          <span class="text-xs px-2.5 py-1 rounded-full border ${confBadgeClass} font-medium block w-max" title="${p.match_explanation}">
            ${p.match_confidence} (${p.similarity_score}%)
          </span>
        </td>
        <td class="py-4 px-4">
          <span class="text-xs px-2.5 py-0.5 rounded-full border ${badgeSourceClass} font-medium">
            ${badgeSourceLabel}
          </span>
        </td>
        <td class="py-4 px-4 text-right">
          <a href="${p.url}" target="_blank" rel="noopener noreferrer" class="p-2 rounded-lg bg-zinc-800 hover:bg-emerald-500 hover:text-slate-950 text-slate-300 inline-block transition-colors">
            <i data-lucide="external-link" class="w-4 h-4"></i>
          </a>
        </td>
      `;
      productsTableBody.appendChild(tr);
    });
    lucide.createIcons();
  }

  // View Mode Toggles
  viewCardsBtn.addEventListener('click', () => {
    state.viewMode = 'cards';
    viewCardsBtn.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-500 text-slate-950 flex items-center space-x-1.5';
    viewTableBtn.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold bg-zinc-800 text-slate-400 hover:text-white flex items-center space-x-1.5';
    applyLocalFiltersAndRender();
  });

  viewTableBtn.addEventListener('click', () => {
    state.viewMode = 'table';
    viewTableBtn.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-500 text-slate-950 flex items-center space-x-1.5';
    viewCardsBtn.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold bg-zinc-800 text-slate-400 hover:text-white flex items-center space-x-1.5';
    applyLocalFiltersAndRender();
  });

  // Sorting and Filters Listeners
  sortSelect.addEventListener('change', (e) => {
    state.sortBy = e.target.value;
    applyLocalFiltersAndRender();
  });

  brandFilterSelect.addEventListener('change', (e) => {
    state.brandFilter = e.target.value;
    applyLocalFiltersAndRender();
  });

  confidenceFilterSelect.addEventListener('change', (e) => {
    state.confidenceFilter = e.target.value;
    applyLocalFiltersAndRender();
  });

  filterColor.addEventListener('input', () => applyLocalFiltersAndRender());
  filterSize.addEventListener('input', () => applyLocalFiltersAndRender());
  filterMinPrice.addEventListener('input', () => applyLocalFiltersAndRender());
  filterMaxPrice.addEventListener('input', () => applyLocalFiltersAndRender());
  filterStock.addEventListener('change', () => applyLocalFiltersAndRender());

  // Export CSV
  exportCsvBtn.addEventListener('click', async () => {
    const prods = getFilteredAndSortedProducts();
    if (prods.length === 0) {
      alert('No hay productos disponibles para exportar.');
      return;
    }
    try {
      await API.exportCsv(prods);
    } catch (err) {
      alert(`Error al exportar CSV: ${err.message}`);
    }
  });

  // History Modal Logic
  openHistoryBtn.addEventListener('click', async () => {
    historyModal.classList.remove('hidden');
    try {
      const items = await API.getHistory();
      renderHistoryList(items);
    } catch (err) {
      historyList.innerHTML = `<p class="text-rose-400 text-sm">${err.message}</p>`;
    }
  });

  closeHistoryBtn.addEventListener('click', () => {
    historyModal.classList.add('hidden');
  });

  clearHistoryBtn.addEventListener('click', async () => {
    if (!confirm('¿Deseas vaciar todo el historial de búsquedas?')) return;
    try {
      await API.clearHistory();
      historyList.innerHTML = '<p class="text-slate-400 text-sm text-center py-6">El historial está vacío.</p>';
    } catch (err) {
      alert(err.message);
    }
  });

  function renderHistoryList(items) {
    if (!items || items.length === 0) {
      historyList.innerHTML = '<p class="text-slate-400 text-sm text-center py-6">No hay búsquedas registradas aún.</p>';
      return;
    }
    historyList.innerHTML = '';
    items.forEach(it => {
      const div = document.createElement('div');
      div.className = 'glass-card p-3 rounded-xl flex items-center justify-between hover:border-emerald-500/40 cursor-pointer transition-all';
      div.innerHTML = `
        <div>
          <div class="flex items-center space-x-2">
            <span class="font-bold text-white text-sm">"${it.query}"</span>
            <span class="text-[10px] px-2 py-0.5 rounded-full bg-zinc-800 text-slate-300 font-mono">${it.competitors}</span>
            ${it.demo_mode ? '<span class="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400">Demo</span>' : ''}
          </div>
          <p class="text-xs text-slate-400 mt-1">
            ${it.total_results} resultados • Promedio: ${formatCOP(it.avg_price)} • ${formatDate(it.created_at)}
          </p>
        </div>
        <button class="px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500 hover:text-slate-950 text-xs font-semibold transition-colors">
          Cargar
        </button>
      `;
      div.addEventListener('click', () => {
        searchInput.value = it.query;
        state.demoMode = it.demo_mode;
        demoModeToggle.checked = it.demo_mode;
        if (it.demo_mode) demoBanner.classList.remove('hidden');
        else demoBanner.classList.add('hidden');
        historyModal.classList.add('hidden');
        executeSearch();
      });
      historyList.appendChild(div);
    });
  }

  // Manual Product Entry Modal Logic
  openManualBtn.addEventListener('click', () => {
    manualModal.classList.remove('hidden');
    document.getElementById('manual-query').value = state.query || searchInput.value || 'Camiseta';
  });

  closeManualBtn.addEventListener('click', () => {
    manualModal.classList.add('hidden');
  });

  manualForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = document.getElementById('manual-query').value.trim();
    const competitor = document.getElementById('manual-competitor').value;
    const title = document.getElementById('manual-title').value.trim();
    const price_cop = parseFloat(document.getElementById('manual-price').value);
    const original_price_cop = document.getElementById('manual-orig-price').value ? parseFloat(document.getElementById('manual-orig-price').value) : null;
    const url = document.getElementById('manual-url').value.trim();
    const color = document.getElementById('manual-color').value.trim() || null;
    const sizes = document.getElementById('manual-sizes').value.split(',').map(s => s.trim()).filter(Boolean);

    try {
      await API.addManual({
        query,
        competitor,
        title,
        price_cop,
        original_price_cop,
        url,
        color,
        sizes,
        available: true,
      });
      alert('¡Producto manual registrado con éxito!');
      manualModal.classList.add('hidden');
      manualForm.reset();
      executeSearch();
    } catch (err) {
      alert(`Error al guardar: ${err.message}`);
    }
  });

  // Initial Health Check
  API.getHealth().then(res => {
    console.log('PriceHunter Backend online:', res);
  }).catch(err => {
    console.warn('Backend not responding yet:', err);
  });

  // Initialize Lucide icons
  lucide.createIcons();
});
