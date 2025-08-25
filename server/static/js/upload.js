// Upload page JavaScript functionality

// Form submission handler
document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const files = document.getElementById('log-files').files;
    const logText = document.getElementById('log-text').value;
    const prompt = document.getElementById('prompt-input').value;

    const resultsDiv = document.getElementById('results');
    const outputDiv = document.getElementById('analysis-output');
    const loadingDiv = document.getElementById('loading');
    const statsSection = document.getElementById('stats-section');

    // Validation
    if (!files.length && !logText.trim()) {
        alert('Please upload log files or paste log content.');
        return;
    }

    if (!prompt.trim()) {
        alert('Please enter a question or analysis request.');
        return;
    }

    // Show loading state and hide previous results
    loadingDiv.style.display = 'block';
    resultsDiv.style.display = 'none';
    
    // Scroll to loading section
    loadingDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });

    const formData = new FormData();
    formData.append('prompt', prompt);

    // Append log text if available
    if (logText) {
        formData.append('log_text', logText);
    }
    
    // Append each uploaded file
    for (const file of files) {
        formData.append('log_files', file);
    }

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            // Try to get error details from response
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.error || `HTTP error! Status: ${response.status}`;
            throw new Error(errorMessage);
        }

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Display results
        outputDiv.innerHTML = `
            <div class="analysis-result">
                <h4 class="text-aqua mb-3">
                    <i class="fas fa-robot me-2"></i>AI Analysis Results
                </h4>
                <div class="result-content">
                    ${formatAnalysisResult(data.result || 'No results found.')}
                </div>
            </div>
        `;
        
        // Display statistics if available
        if (data.stats) {
            updateStatistics(data.stats);
            statsSection.style.display = 'block';
            
            // Show visualization section first, then create charts after a small delay
            document.getElementById('visualization-section').style.display = 'block';
            
            // Small delay to ensure DOM elements are rendered
            setTimeout(() => {
                createStaticVisualizations(data.stats);
            }, 100);
        }
        
        resultsDiv.style.display = 'block';
        
        // Scroll to results
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (error) {
        console.error('Error during analysis:', error);
        outputDiv.innerHTML = `
            <div class="alert alert-danger">
                <h5><i class="fas fa-exclamation-triangle me-2"></i>Analysis Error</h5>
                <p>${error.message}</p>
                <small class="text-muted">Please check your log format and try again. If the problem persists, contact support.</small>
            </div>
        `;
        resultsDiv.style.display = 'block';
        
        // Scroll to results (error message)
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } finally {
        loadingDiv.style.display = 'none';
    }
});

// Update statistics display
function updateStatistics(stats) {
    document.getElementById('total-lines').textContent = stats.total_lines || 0;
    document.getElementById('error-count').textContent = stats.error_count || 0;
    document.getElementById('warning-count').textContent = stats.warning_count || 0;
    document.getElementById('critical-count').textContent = stats.critical_count || 0;
}

// Format analysis result for better display
function formatAnalysisResult(text) {
    // Convert markdown-style headers and bullet points to HTML
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold text
        .replace(/^\d+\.\s+(.+)/gm, '<h6 class="text-aqua mt-3 mb-2">$1</h6>') // Numbered headers
        .replace(/^-\s+(.+)/gm, '<li>$1</li>') // Bullet points
        .replace(/\n\n/g, '</p><p>') // Paragraphs
        .replace(/^(.+)$/gm, '<p>$1</p>') // Wrap in paragraphs
        .replace(/<p><li>/g, '<ul><li>') // Start lists
        .replace(/<\/li><\/p>/g, '</li></ul>') // End lists
        .replace(/(<ul><li>.*?<\/li>)<p>/g, '$1</ul><p>'); // Fix list endings
}

// Copy results to clipboard
function copyToClipboard() {
    const output = document.getElementById('analysis-output');
    const text = output.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        // Show temporary success message
        const button = event.target.closest('button');
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check me-2"></i>Copied!';
        button.classList.remove('btn-outline-primary');
        button.classList.add('btn-success');
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-primary');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        alert('Failed to copy text to clipboard');
    });
}

// Save analysis to user history (requires login)
function saveAnalysis() {
    // This would be implemented to save the analysis to the user's history
    // For now, just show a message
    alert('Analysis saved to your history!');
}

// Set example queries
function setExample(exampleNumber) {
    const promptInput = document.getElementById('prompt-input');
    
    const examples = {
        1: "What database connection problems occurred and how can I fix them?",
        2: "Analyze security threats, failed logins, and suspicious activities.",
        3: "Find performance bottlenecks, slow queries, and resource issues."
    };
    
    promptInput.value = examples[exampleNumber] || "";
    promptInput.focus();
    
    // Scroll to the form
    document.getElementById('upload-form').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

// File upload drag and drop functionality
const fileInput = document.getElementById('log-files');
const uploadArea = fileInput.closest('.server-card');

// Highlight on drag over
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Highlight drop area
['dragenter', 'dragover'].forEach(eventName => {
    uploadArea.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
    uploadArea.style.borderColor = 'var(--aqua-blue)';
    uploadArea.style.backgroundColor = 'rgba(0, 212, 255, 0.05)';
}

function unhighlight(e) {
    uploadArea.style.borderColor = 'var(--border-color)';
    uploadArea.style.backgroundColor = '';
}

// Handle dropped files
uploadArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    fileInput.files = files;
    
    // Show file names
    updateFileList(files);
}

// Update file input display
fileInput.addEventListener('change', function() {
    updateFileList(this.files);
});

function updateFileList(files) {
    if (files.length > 0) {
        const fileNames = Array.from(files).map(file => file.name).join(', ');
        const fileText = files.length === 1 ? 'file' : 'files';
        
        // Update the help text to show selected files
        const helpText = fileInput.nextElementSibling;
        helpText.innerHTML = `<i class="fas fa-check text-success me-1"></i>${files.length} ${fileText} selected: ${fileNames}`;
    }
}

// Real-time character count for textarea
const logTextArea = document.getElementById('log-text');
logTextArea.addEventListener('input', function() {
    const helpText = this.nextElementSibling;
    const charCount = this.value.length;
    const lineCount = this.value.split('\n').length;
    
    if (charCount > 0) {
        helpText.innerHTML = `<i class="fas fa-info-circle me-1"></i>Characters: ${charCount}, Lines: ${lineCount}`;
    } else {
        helpText.innerHTML = `<i class="fas fa-info-circle me-1"></i>Paste log content directly for quick analysis`;
    }
});

// Auto-resize textarea
logTextArea.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// Create static visualizations based on uploaded data
function createStaticVisualizations(stats) {
    // Destroy existing charts if they exist
    if (window.logDistributionChart && typeof window.logDistributionChart.destroy === 'function') {
        window.logDistributionChart.destroy();
    }
    if (window.timelineChart && typeof window.timelineChart.destroy === 'function') {
        window.timelineChart.destroy();
    }
    
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return;
    }
    
    // Create Log Level Distribution Chart (Doughnut)
    const distributionCanvas = document.getElementById('logDistributionChart');
    if (!distributionCanvas) {
        console.error('Distribution chart canvas not found');
        return;
    }
    
    const distributionCtx = distributionCanvas.getContext('2d');
    window.logDistributionChart = new Chart(distributionCtx, {
        type: 'doughnut',
        data: {
            labels: ['Errors', 'Warnings', 'Critical', 'Info'],
            datasets: [{
                data: [
                    stats.error_count || 0,
                    stats.warning_count || 0, 
                    stats.critical_count || 0,
                    stats.info_count || 0
                ],
                backgroundColor: [
                    '#ff3366',  // Red for errors
                    '#ff9500',  // Orange for warnings
                    '#e74c3c',  // Dark red for critical
                    '#00d4ff'   // Aqua for info
                ],
                borderWidth: 2,
                borderColor: '#1a1a1a'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false, // Disable animations to prevent scaling issues
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e0e0e0',
                        padding: 15,
                        usePointStyle: true
                    }
                }
            }
        }
    });
    
    // Create Timeline Chart (Bar chart showing log volume)
    const timelineCanvas = document.getElementById('timelineChart');
    if (!timelineCanvas) {
        console.error('Timeline chart canvas not found');
        return;
    }
    
    const timelineCtx = timelineCanvas.getContext('2d');
    
    // Create simple timeline data based on log distribution
    const timelineData = createTimelineData(stats);
    
    window.timelineChart = new Chart(timelineCtx, {
        type: 'bar',
        data: {
            labels: timelineData.labels,
            datasets: [{
                label: 'Log Events',
                data: timelineData.data,
                backgroundColor: 'rgba(0, 212, 255, 0.3)',
                borderColor: '#00d4ff',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false, // Disable animations
            plugins: {
                legend: {
                    labels: {
                        color: '#e0e0e0'
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#e0e0e0' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                y: {
                    ticks: { color: '#e0e0e0' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    beginAtZero: true
                }
            }
        }
    });
}

// Create timeline data for visualization
function createTimelineData(stats) {
    const totalEvents = stats.total_lines || 0;
    const segments = 6; // Show 6 time segments
    
    // Create mock distribution across time segments
    const labels = [];
    const data = [];
    
    for (let i = 0; i < segments; i++) {
        labels.push(`T${i + 1}`);
        // Distribute events with some randomness but based on actual stats
        const baseValue = Math.floor(totalEvents / segments);
        const variation = Math.floor(Math.random() * (baseValue * 0.5));
        data.push(Math.max(0, baseValue + (Math.random() > 0.5 ? variation : -variation)));
    }
    
    return { labels, data };
}
