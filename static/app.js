// Global state
let currentCalendar = null;
let currentRequest = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('calendarForm').addEventListener('submit', handleFormSubmit);
});

// Add persona field
function addPersona() {
    const container = document.getElementById('personasContainer');
    const personaDiv = document.createElement('div');
    personaDiv.className = 'persona-item';
    personaDiv.innerHTML = `
        <div class="form-group">
            <label>Name *</label>
            <input type="text" class="persona-name" required>
        </div>
        <div class="form-group">
            <label>Reddit Username *</label>
            <input type="text" class="persona-username" placeholder="e.g., riley_ops" required>
        </div>
        <div class="form-group">
            <label>Role *</label>
            <input type="text" class="persona-role" required>
        </div>
        <div class="form-group">
            <label>Voice/Style *</label>
            <textarea class="persona-voice" rows="2" required></textarea>
        </div>
        <div class="form-group">
            <label>Interests (comma-separated) *</label>
            <input type="text" class="persona-interests" required>
        </div>
        <div class="form-group">
            <label>Posting Style *</label>
            <textarea class="persona-posting-style" rows="2" required></textarea>
        </div>
        <button type="button" class="btn btn-danger btn-small" onclick="removePersona(this)">Remove</button>
    `;
    container.appendChild(personaDiv);
}

// Remove persona field
function removePersona(button) {
    const personas = document.querySelectorAll('.persona-item');
    if (personas.length > 1) {
        button.closest('.persona-item').remove();
    } else {
        alert('You need at least one persona!');
    }
}

// Load sample data
async function loadSampleData() {
    try {
        const response = await fetch('/api/sample-data');
        const data = await response.json();
        
        // Fill company info
        document.getElementById('companyName').value = data.company_info.name;
        document.getElementById('companyWebsite').value = data.company_info.website;
        document.getElementById('companyDescription').value = data.company_info.description;
        document.getElementById('targetAudience').value = data.company_info.target_audience.join(', ');
        document.getElementById('keyFeatures').value = data.company_info.key_features.join(', ');
        document.getElementById('domain').value = data.company_info.domain;
        
        // Fill personas
        const personasContainer = document.getElementById('personasContainer');
        personasContainer.innerHTML = '';
        data.personas.forEach(persona => {
            addPersona();
            const items = personasContainer.querySelectorAll('.persona-item');
            const lastItem = items[items.length - 1];
            lastItem.querySelector('.persona-name').value = persona.name;
            lastItem.querySelector('.persona-username').value = persona.username || '';
            lastItem.querySelector('.persona-role').value = persona.role;
            lastItem.querySelector('.persona-voice').value = persona.voice;
            lastItem.querySelector('.persona-interests').value = persona.interests.join(', ');
            lastItem.querySelector('.persona-posting-style').value = persona.posting_style;
        });
        
        // Fill subreddits
        document.getElementById('subreddits').value = data.subreddits.join(', ');
        
        // Fill keywords
        if (data.keywords && data.keywords.length > 0) {
            const keywordText = data.keywords.map(k => `${k.keyword_id}:${k.keyword}`).join('\n');
            document.getElementById('keywords').value = keywordText;
        } else if (data.chatgpt_queries) {
            // Fallback for old format
            document.getElementById('keywords').value = data.chatgpt_queries.map((q, i) => `K${i+1}:${q}`).join('\n');
        }
        
        // Fill posts per week
        document.getElementById('postsPerWeek').value = data.posts_per_week;
        
        alert('Sample data loaded! Review and click "Generate Calendar" when ready.');
    } catch (error) {
        console.error('Error loading sample data:', error);
        alert('Error loading sample data. Please check the console.');
    }
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    // Show loading
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Generating...';
    submitBtn.disabled = true;
    
    try {
        // Collect form data
        const request = collectFormData();
        
        // Validate
        if (request.personas.length < 2) {
            alert('Please add at least 2 personas!');
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
            return;
        }
        
        // Generate calendar
        const response = await fetch('/api/generate-calendar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(request),
        });
        
        if (!response.ok) {
            // Try to get error details from response
            let errorMessage = `HTTP error! status: ${response.status}`;
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMessage = errorData.detail;
                }
            } catch (e) {
                // If response is not JSON, use status text
                errorMessage = `HTTP error! status: ${response.status} - ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }
        
        const result = await response.json();
        
        // Store for next week generation
        currentCalendar = result;
        currentRequest = request;
        
        // Display results
        displayCalendar(result);
        
        // Scroll to results
        document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('Error generating calendar:', error);
        
        // Show detailed error message
        let errorMessage = 'Error generating calendar.\n\n';
        if (error.message) {
            errorMessage += error.message;
        } else {
            errorMessage += 'Unknown error occurred.';
        }
        
        // Add helpful tips for common errors
        if (errorMessage.includes('Groq API') || errorMessage.includes('GROQ_API_KEY')) {
            errorMessage += '\n\n💡 SOLUTION:\n';
            errorMessage += '1. Check your .env file has GROQ_API_KEY=your_key\n';
            errorMessage += '2. Get a free key at https://console.groq.com/\n';
            errorMessage += '3. Restart the server after updating .env';
        }
        
        alert(errorMessage);
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// Collect form data
function collectFormData() {
    const personas = [];
    document.querySelectorAll('.persona-item').forEach(item => {
        personas.push({
            name: item.querySelector('.persona-name').value,
            username: item.querySelector('.persona-username').value,
            role: item.querySelector('.persona-role').value,
            voice: item.querySelector('.persona-voice').value,
            interests: item.querySelector('.persona-interests').value.split(',').map(s => s.trim()),
            posting_style: item.querySelector('.persona-posting-style').value
        });
    });
    
    // Parse keywords (format: K1:keyword1, K2:keyword2 or one per line)
    const keywordsText = document.getElementById('keywords').value;
    const keywords = [];
    keywordsText.split('\n').forEach(line => {
        const trimmed = line.trim();
        if (trimmed) {
            if (trimmed.includes(':')) {
                const [keyword_id, keyword] = trimmed.split(':').map(s => s.trim());
                keywords.push({ keyword_id, keyword });
            } else {
                // If no colon, generate ID
                keywords.push({ keyword_id: `K${keywords.length + 1}`, keyword: trimmed });
            }
        }
    });
    
    return {
        company_info: {
            name: document.getElementById('companyName').value,
            website: document.getElementById('companyWebsite').value,
            description: document.getElementById('companyDescription').value,
            target_audience: document.getElementById('targetAudience').value.split(',').map(s => s.trim()),
            key_features: document.getElementById('keyFeatures').value.split(',').map(s => s.trim()).filter(s => s),
            domain: document.getElementById('domain').value
        },
        personas: personas,
        subreddits: document.getElementById('subreddits').value.split(',').map(s => s.trim()),
        keywords: keywords,
        posts_per_week: parseInt(document.getElementById('postsPerWeek').value)
    };
}

// Display calendar
function displayCalendar(response) {
    // Handle both direct calendar and response object
    const calendar = response.calendar || response;
    const qualityScore = response.quality_score !== undefined ? response.quality_score : 10.0;
    const warnings = response.warnings || [];
    
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
    
    // Update quality badge
    const badge = document.getElementById('qualityBadge');
    badge.textContent = `Quality Score: ${qualityScore.toFixed(1)}/10`;
    badge.className = 'quality-badge ';
    if (qualityScore >= 8) {
        badge.className += 'excellent';
    } else if (qualityScore >= 6) {
        badge.className += 'good';
    } else if (qualityScore >= 4) {
        badge.className += 'fair';
    } else {
        badge.className += 'poor';
    }
    
    // Display warnings
    const warningsContainer = document.getElementById('warningsContainer');
    if (warnings.length > 0) {
        warningsContainer.className = 'warnings';
        warningsContainer.innerHTML = '<strong>⚠️ Warnings:</strong>' + 
            warnings.map(w => `<div class="warning-item">${w}</div>`).join('');
    } else {
        warningsContainer.className = 'warnings hidden';
    }
    
    // Display calendar info
    const info = document.getElementById('calendarInfo');
    const weekStart = new Date(calendar.week_start);
    const weekEnd = new Date(calendar.week_end);
    info.innerHTML = `
        <strong>Week:</strong> ${weekStart.toLocaleDateString()} - ${weekEnd.toLocaleDateString()}<br>
        <strong>Total Posts:</strong> ${calendar.metadata?.total_posts || 0}<br>
        <strong>Total Replies:</strong> ${calendar.metadata?.total_replies || 0}<br>
        <strong>Subreddits:</strong> ${(calendar.metadata?.subreddits_used || []).join(', ')}
    `;
    
    // Display calendar table
    const tbody = document.getElementById('calendarBody');
    tbody.innerHTML = '';
    
    if (calendar.entries && calendar.entries.length > 0) {
        calendar.entries.forEach(entry => {
            const row = document.createElement('tr');
            const date = new Date(entry.date);
            const entryId = entry.post_id || entry.comment_id || '-';
            const keywordIds = (entry.keyword_ids || []).join(', ') || '-';
            
            row.innerHTML = `
                <td>${entryId}</td>
                <td>${date.toLocaleDateString()}</td>
                <td>${entry.time || date.toLocaleTimeString()}</td>
                <td><span class="type-badge ${entry.type}">${entry.type}</span></td>
                <td>${entry.username || entry.persona}</td>
                <td>r/${entry.subreddit}</td>
                <td>${entry.title || '-'}</td>
                <td class="content-full">${entry.content}</td>
                <td>${keywordIds}</td>
            `;
            tbody.appendChild(row);
        });
    } else {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 20px;">No entries in calendar</td></tr>';
    }
}

// Generate next week
async function generateNextWeek() {
    if (!currentRequest || !currentCalendar) {
        alert('Please generate a calendar first!');
        return;
    }
    
    const btn = event.target;
    const originalText = btn.textContent;
    btn.textContent = 'Generating...';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/generate-next-week', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                request: currentRequest,
                current_week_start: (currentCalendar.calendar || currentCalendar).week_start
            }),
        });
        
        if (!response.ok) {
            // Try to get error details from response
            let errorMessage = `HTTP error! status: ${response.status}`;
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMessage = errorData.detail;
                }
            } catch (e) {
                // If response is not JSON, use status text
                errorMessage = `HTTP error! status: ${response.status} - ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }
        
        const result = await response.json();
        currentCalendar = result;
        currentRequest = data.request; // Update request for next iteration
        displayCalendar(result);
        
        // Scroll to top of results
        document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('Error generating next week:', error);
        alert('Error generating next week: ' + error.message);
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

// Export calendar
function exportCalendar() {
    if (!currentCalendar) {
        alert('No calendar to export!');
        return;
    }
    
    const dataStr = JSON.stringify(currentCalendar, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `reddit-calendar-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
}

// Reset form
function resetForm() {
    document.getElementById('calendarForm').reset();
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('personasContainer').innerHTML = '';
    addPersona();
    addPersona();
    currentCalendar = null;
    currentRequest = null;
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

