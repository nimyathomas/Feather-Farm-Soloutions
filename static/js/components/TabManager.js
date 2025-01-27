export class TabManager {
    constructor(options = {}) {
        this.options = {
            activeClass: 'active',
            ...options
        };
        this.initializeTabs();
    }

    initializeTabs() {
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => this.switchTab(button));
        });
    }

    switchTab(selectedButton) {
        this.deactivateAllTabs();
        this.activateTab(selectedButton);
    }

    deactivateAllTabs() {
        document.querySelectorAll('.tab-button').forEach(btn => 
            btn.classList.remove(this.options.activeClass)
        );
        document.querySelectorAll('.tab-pane').forEach(pane => 
            pane.classList.remove(this.options.activeClass)
        );
    }

    activateTab(button) {
        button.classList.add(this.options.activeClass);
        const tabId = button.getAttribute('data-tab');
        document.getElementById(tabId)?.classList.add(this.options.activeClass);
    }
} 