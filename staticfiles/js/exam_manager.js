

class ExamManager {
    constructor(sessionId, wsUrl) {
        this.sessionId = sessionId;
        this.wsUrl = wsUrl;
        this.apiEndpoint = `/sms/api/exam/${sessionId}/questions/`;
        this.form = document.getElementById('exam-form');
        this.questionsContainer = document.getElementById('questions-container');
        this.heartbeatStatus = document.getElementById('heartbeat-status');
        this.heartbeatInterval = null;
        this.websocket = null;
    }

    init() {
        this.fetchQuestions();
        this.setupWebSocket();
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
    }

    // --- 1. ASYNCHRONOUS DATA FETCH (API) ---
    async fetchQuestions() {
        try {
            const response = await fetch(this.apiEndpoint);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            
            // Hide loading, show form
            document.getElementById('exam-loading').classList.add('hidden');
            this.form.classList.remove('hidden');

            this.renderQuestions(data.questions);
            // Example: update the subject title
            document.getElementById('subject-title').textContent = `(Session ${this.sessionId})`;
            
        } catch (error) {
            console.error("Error fetching exam questions:", error);
            alert("Could not load exam. Please check your connection.");
        }
    }

    renderQuestions(questions) {
        // Aesthetic Tailwind rendering of the questions and randomized options
        this.questionsContainer.innerHTML = questions.map((q, index) => {
            // q.randomized_options is an array of [index, option_text]
            const optionsHtml = q.randomized_options.map(([opt_index, opt_text]) => `
                <label class="block p-4 border border-gray-200 rounded-lg cursor-pointer hover:bg-blue-50 transition duration-150">
                    <input type="radio" 
                           name="question_${q.id}" 
                           value="${opt_index}" 
                           class="mr-3 text-blue-600 focus:ring-blue-500"
                           required>
                    <span class="font-medium text-gray-700">${opt_text}</span>
                </label>
            `).join('');

            return `
                <div class="question-card p-6 bg-white border border-gray-100 rounded-xl shadow-sm">
                    <p class="text-xl font-semibold text-gray-800 mb-4">${index + 1}. ${q.question_text}</p>
                    <div class="space-y-3">
                        ${optionsHtml}
                    </div>
                </div>
            `;
        }).join('');
    }

    // --- 2. ASYNCHRONOUS REAL-TIME (CHANNELS HEARTBEAT) ---
    setupWebSocket() {
        // Use wss:// for production (secure) or ws:// for local development
        this.websocket = new WebSocket(this.wsUrl.replace('http', 'ws'));

        this.websocket.onopen = () => {
            console.log("WebSocket connected. Starting heartbeat.");
            this.updateStatus(true);
            this.startHeartbeat();
        };

        this.websocket.onclose = () => {
            console.warn("WebSocket closed. Attempting to reconnect in 5s...");
            this.updateStatus(false);
            // Add reconnection logic here for production robustness
            setTimeout(() => this.setupWebSocket(), 5000); 
        };

        this.websocket.onerror = (error) => {
            console.error("WebSocket error:", error);
            this.updateStatus(false);
        };
        
        // This receives messages from the server (e.g., admin forcing submission)
        this.websocket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            console.log("Received server message:", data);
            if (data.type === 'status_update' && data.message === 'force_submit') {
                alert("The exam has been submitted by an administrator due to inactivity.");
                this.handleSubmit(null, true); // Force submit
            }
        };
    }

    startHeartbeat() {
        // Send a simple 'heartbeat' message to the consumer every 10 seconds
        this.heartbeatInterval = setInterval(() => {
            if (this.websocket.readyState === WebSocket.OPEN) {
                this.websocket.send(JSON.stringify({
                    'status': 'active',
                    'timestamp': Date.now()
                }));
            }
        }, 10000); // 10 seconds
    }

    updateStatus(isConnected) {
        if (isConnected) {
            this.heartbeatStatus.textContent = "Status: Connected 🟢";
            this.heartbeatStatus.className = "px-4 py-2 text-sm rounded-full bg-green-100 text-green-700 font-semibold";
        } else {
            this.heartbeatStatus.textContent = "Status: Disconnected 🔴";
            this.heartbeatStatus.className = "px-4 py-2 text-sm rounded-full bg-red-100 text-red-700 font-semibold";
        }
    }

    handleSubmit(event, isForced = false) {
        if (event) {
            event.preventDefault();
        }

        if (!confirm(isForced ? "Your exam has been submitted by the system." : "Are you sure you want to submit the exam?")) {
            return;
        }

        clearInterval(this.heartbeatInterval);
        this.websocket.close();
        
        // TODO: Implement the final POST request here to the submission API endpoint
        alert("Exam submitted! (Submission API endpoint not yet implemented)"); 
        // Window.location.href = '/sms/results/';
    }
}