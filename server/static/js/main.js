document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const files = document.getElementById('log-files').files;
    const logText = document.getElementById('log-text').value;
    const prompt = document.getElementById('prompt-input').value;

    const resultsDiv = document.getElementById('results');
    const outputDiv = document.getElementById('analysis-output');
    const loadingDiv = document.getElementById('loading');

    // Show loading state and hide previous results
    loadingDiv.style.display = 'block';
    resultsDiv.style.display = 'none';

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
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        
        // Display results
        outputDiv.textContent = data.result || 'No results found.';
        resultsDiv.style.display = 'block';

    } catch (error) {
        console.error('Error during analysis:', error);
        outputDiv.textContent = `Error: ${error.message}. Please try again.`;
        resultsDiv.style.display = 'block';
    } finally {
        loadingDiv.style.display = 'none';
    }
});