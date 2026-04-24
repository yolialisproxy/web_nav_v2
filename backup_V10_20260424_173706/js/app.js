window.SITES = window.SITES || [];
        const sitesEl = document.getElementById('sites');
        const searchEl = document.getElementById('search');
        const catEl = document.getElementById('category-list');

        function renderSites(list) {
            sitesEl.innerHTML = list.map(site => `
            <a href="${site.url}" target="_blank" rel="noopener" class="site-card bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-all hover:-translate-y-1 block flex flex-col gap-3">
                <div class="flex items-center gap-3">
                    <img src="https://www.google.com/s2/favicons?domain=${new URL(site.url).hostname}&sz=64"
                         alt="${site.title} favicon"
                         class="card-icon w-8 h-8 rounded object-contain shrink-0"
                         onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22 fill=%22%236b7280%22><path d=%22M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z%22/></svg>'">
                    <div class="card-title font-bold text-base truncate">${site.title}</div>
                </div>
                <div class="card-desc text-sm text-gray-500 mt-1 line-clamp-2 overflow-hidden">${site.description || ''}</div>
            </a>
            `).join('');
        }

        function renderCategories() {
            const cats = [...new Set(window.SITES.map(s => s.category))].sort();
            catEl.innerHTML = cats.map(cat => `
            <button class="w-full text-left px-3 py-2 rounded hover:bg-gray-100 transition-colors" data-category="${cat}">${cat}</button>
            `).join('');

            // Category click filtering
            catEl.querySelectorAll('button').forEach(btn => {
                btn.addEventListener('click', e => {
                    // Clear active state
                    catEl.querySelectorAll('button').forEach(b => b.classList.remove('bg-blue-50', 'text-blue-700', 'font-medium'));
                    // Set active state
                    btn.classList.add('bg-blue-50', 'text-blue-700', 'font-medium');
                    // Filter sites
                    const selectedCat = btn.dataset.category;
                    renderSites(window.SITES.filter(s => s.category === selectedCat));
                    // Scroll to top
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                });
            });
        }

        searchEl.addEventListener('input', e => {
            const q = e.target.value.toLowerCase();
            renderSites(window.SITES.filter(s =>
                s.title.toLowerCase().includes(q) || s.description?.toLowerCase().includes(q)
            ));
        });

        renderCategories();
        renderSites(window.SITES);

        // Sidebar Toggle Functionality
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('main-content');
        const toggleIcon = sidebarToggle.querySelector('i');

        function setSidebarState(collapsed) {
            if (collapsed) {
                sidebar.classList.add('w-0', 'lg:w-0', 'opacity-0');
                sidebar.classList.remove('w-64', 'lg:w-64');
                toggleIcon.className = 'fas fa-angles-right';
                localStorage.setItem('sidebar_collapsed', 'true');
            } else {
                sidebar.classList.remove('w-0', 'lg:w-0', 'opacity-0');
                sidebar.classList.add('w-64', 'lg:w-64');
                toggleIcon.className = 'fas fa-bars';
                localStorage.setItem('sidebar_collapsed', 'false');
            }
        }

        // Load saved state on page load
        const savedState = localStorage.getItem('sidebar_collapsed');
        if (savedState === 'true') {
            setSidebarState(true);
        }

        sidebarToggle.addEventListener('click', () => {
            const isCollapsed = sidebar.classList.contains('w-0');
            setSidebarState(!isCollapsed);
        });