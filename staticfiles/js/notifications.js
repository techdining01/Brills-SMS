/**
 * WebSocket Notification Client
 * Handles real-time notifications via Django Channels
 */

class NotificationManager {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000; // 3 seconds
        this.unreadCount = 0;
    }

    /**
     * Initialize WebSocket connection
     */
    init() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const path = `${protocol}//${window.location.host}/ws/notifications/`;
        
        console.log('Connecting to WebSocket:', path);
        
        this.ws = new WebSocket(path);
        
        this.ws.onopen = (e) => this.onOpen(e);
        this.ws.onclose = (e) => this.onClose(e);
        this.ws.onerror = (e) => this.onError(e);
        this.ws.onmessage = (e) => this.onMessage(e);
    }

    /**
     * WebSocket opened
     */
    onOpen(event) {
        console.log('WebSocket connection established');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        
        // Fetch initial unread count
        this.fetchUnreadCount();
    }

    /**
     * WebSocket closed
     */
    onClose(event) {
        console.log('WebSocket connection closed');
        this.isConnected = false;
        
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            const delay = this.reconnectDelay * (this.reconnectAttempts + 1);
            console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts + 1})`);
            setTimeout(() => {
                this.reconnectAttempts++;
                this.init();
            }, delay);
        }
    }

    /**
     * WebSocket error
     */
    onError(event) {
        console.error('WebSocket error:', event);
    }

    /**
     * WebSocket message received
     */
    onMessage(event) {
        const data = JSON.parse(event.data);
        
        switch (data.type) {
            case 'notification':
                this.handleNotification(data);
                break;
            case 'unread_count':
                this.handleUnreadCountUpdate(data);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    /**
     * Handle incoming notification
     */
    handleNotification(data) {
        console.log('New notification:', data);
        
        // Update unread count
        this.unreadCount++;
        this.updateNotificationBadge();
        
        // Show toast notification
        this.showToast(data);
        
        // Add to notifications list (if page is open)
        this.addNotificationToDOM(data);
        
        // Play sound if enabled
        this.playNotificationSound();
    }

    /**
     * Handle unread count update
     */
    handleUnreadCountUpdate(data) {
        this.unreadCount = data.count;
        this.updateNotificationBadge();
    }

    /**
     * Update notification badge in navbar
     */
    updateNotificationBadge() {
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            if (this.unreadCount > 0) {
                badge.textContent = this.unreadCount;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    /**
     * Show toast notification
     */
    showToast(data) {
        // Create toast HTML
        const toastHTML = `
            <div class="toast-notification toast-${data.category}">
                <div class="toast-header">
                    <strong>${data.title}</strong>
                    <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
                </div>
                <div class="toast-body">
                    ${data.message}
                </div>
            </div>
        `;
        
        // Add to toast container
        const container = document.querySelector('.notification-toast-container') || 
                         this.createToastContainer();
        const toast = document.createElement('div');
        toast.innerHTML = toastHTML;
        container.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    /**
     * Create toast container if it doesn't exist
     */
    createToastContainer() {
        const container = document.createElement('div');
        container.className = 'notification-toast-container';
        document.body.appendChild(container);
        return container;
    }

    /**
     * Add notification to DOM list (if page is open)
     */
    addNotificationToDOM(data) {
        const list = document.querySelector('#notificationList');
        if (!list) return;
        
        const itemHTML = `
            <div class="notification-item unread" data-id="${data.id}">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="notification-title">
                            <span class="badge badge-${data.category}">
                                ${this.getCategoryIcon(data.category)}
                            </span>
                            ${data.title}
                            <span class="unread-indicator"></span>
                        </h6>
                        <p class="notification-message mb-2">${data.message}</p>
                        <small class="text-muted">just now</small>
                    </div>
                    <div class="notification-actions">
                        <button class="btn btn-sm btn-outline-secondary" onclick="notificationManager.markAsRead(${data.id})">
                            <i class="bi bi-check"></i> Read
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        list.insertAdjacentHTML('afterbegin', itemHTML);
    }

    /**
     * Get icon for category
     */
    getCategoryIcon(category) {
        const icons = {
            'info': '<i class="bi bi-info-circle"></i>',
            'success': '<i class="bi bi-check-circle"></i>',
            'warning': '<i class="bi bi-exclamation-triangle"></i>',
            'error': '<i class="bi bi-x-circle"></i>'
        };
        return icons[category] || icons['info'];
    }

    /**
     * Play notification sound
     */
    playNotificationSound() {
        // Only if user has notification sounds enabled
        if (localStorage.getItem('notification_sound_enabled') !== 'false') {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAAB9AAACABAAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj==');
            audio.play().catch(e => console.log('Could not play sound:', e));
        }
    }

    /**
     * Mark notification as read
     */
    markAsRead(notificationId) {
        // Send to server via WebSocket
        if (this.isConnected) {
            this.ws.send(JSON.stringify({
                type: 'mark_as_read',
                notification_id: notificationId
            }));
        }
        
        // Update UI
        const item = document.querySelector(`[data-id="${notificationId}"]`);
        if (item) {
            item.classList.remove('unread');
            const btn = item.querySelector('.notification-actions button');
            if (btn) btn.style.display = 'none';
        }
        
        // Update count
        this.unreadCount = Math.max(0, this.unreadCount - 1);
        this.updateNotificationBadge();
    }

    /**
     * Fetch unread count from server
     */
    fetchUnreadCount() {
        fetch('/api/notifications/unread/')
            .then(response => response.json())
            .then(data => {
                this.unreadCount = data.count;
                this.updateNotificationBadge();
            })
            .catch(e => console.error('Error fetching unread count:', e));
    }
}

// Initialize notification manager when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.notificationManager = new NotificationManager();
    window.notificationManager.init();
});
