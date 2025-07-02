// WebSocket connection for real-time updates
class WebSocketManager {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.connect();
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/dashboard/`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = (event) => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
            this.showConnectionStatus('Connected', 'success');
        };
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.socket.onclose = (event) => {
            console.log('WebSocket disconnected');
            this.showConnectionStatus('Disconnected', 'warning');
            this.attemptReconnect();
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showConnectionStatus('Connection Error', 'danger');
        };
    }

    handleMessage(data) {
        switch (data.type) {
            case 'dashboard_update':
                this.updateDashboard(data.data);
                break;
            case 'complaint_update':
                this.handleComplaintUpdate(data);
                break;
            case 'new_complaint':
                this.handleNewComplaint(data);
                break;
            case 'notification':
                this.showNotification(data.message, data.notification_type);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    updateDashboard(data) {
        if (data.type === 'admin_dashboard') {
            // Update admin dashboard statistics
            this.updateElement('total-employees', data.total_employees);
            this.updateElement('total-complaints', data.total_complaints);
            this.updateElement('pending-complaints', data.pending_complaints);
            this.updateElement('in-progress-complaints', data.in_progress_complaints);
            this.updateElement('closed-complaints', data.closed_complaints);
            this.updateElement('escalated-complaints', data.escalated_complaints);
        } else if (data.type === 'employee_dashboard') {
            // Update employee dashboard statistics
            this.updateElement('assigned-complaints', data.assigned_complaints);
            this.updateElement('pending-assigned', data.pending_assigned);
            this.updateElement('in-progress-assigned', data.in_progress_assigned);
            this.updateElement('closed-assigned', data.closed_assigned);
        }
        
        // Add visual feedback
        this.highlightUpdatedElements();
    }

    handleComplaintUpdate(data) {
        // Handle complaint status updates
        this.showNotification(`Complaint ${data.action}: ${data.message}`, 'info');
        
        // Refresh complaint list if on complaints page
        if (window.location.pathname.includes('complaints')) {
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
    }

    handleNewComplaint(data) {
        // Handle new complaint notifications
        this.showNotification(`New complaint: ${data.complaint.title}`, 'success');
        
        // Refresh dashboard if on dashboard page
        if (window.location.pathname === '/dashboard/') {
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            const oldValue = element.textContent;
            element.textContent = value;
            
            // Add animation class
            element.classList.add('updated');
            setTimeout(() => {
                element.classList.remove('updated');
            }, 2000);
        }
    }

    highlightUpdatedElements() {
        const elements = document.querySelectorAll('.updated');
        elements.forEach(element => {
            element.style.backgroundColor = '#fff3cd';
            element.style.transition = 'background-color 0.5s ease';
            
            setTimeout(() => {
                element.style.backgroundColor = '';
            }, 2000);
        });
    }

    showNotification(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        // Add to toast container
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.appendChild(toast);
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    showConnectionStatus(message, type) {
        // Show connection status in a subtle way
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `badge bg-${type}`;
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
        } else {
            console.log('Max reconnection attempts reached');
            this.showConnectionStatus('Connection Failed', 'danger');
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
        }
    }
}

// Initialize WebSocket when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.webSocketManager = new WebSocketManager();
    
    // Clean up on page unload
    window.addEventListener('beforeunload', function() {
        if (window.webSocketManager) {
            window.webSocketManager.disconnect();
        }
    });
}); 