// Tab Management
class TabManager {
    constructor() {
        this.initializeTabs();
    }

    initializeTabs() {
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => this.switchTab(button));
        });
    }

    switchTab(selectedButton) {
        // Remove active class from all buttons
        document.querySelectorAll('.tab-button').forEach(btn => 
            btn.classList.remove('active')
        );
        
        // Add active class to selected button
        selectedButton.classList.add('active');
        
        // Switch tab content
        const tabId = selectedButton.getAttribute('data-tab');
        document.querySelectorAll('.tab-pane').forEach(pane => 
            pane.classList.remove('active')
        );
        document.getElementById(tabId).classList.add('active');
    }
}

// Modal Management
class EnquiryModal {
    constructor() {
        this.modal = document.getElementById('enquiryModal');
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Close button click
        document.querySelector('.close-btn').addEventListener('click', 
            () => this.close()
        );

        // Click outside modal
        window.addEventListener('click', (event) => {
            if (event.target === this.modal) {
                this.close();
            }
        });
    }

    open() {
        this.modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    close() {
        this.modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    new TabManager();
    window.enquiryModal = new EnquiryModal();
}); 