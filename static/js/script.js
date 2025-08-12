// DOM Elements
const predictionForm = document.getElementById('predictionForm');
const loading = document.getElementById('loading');
const results = document.getElementById('results');

// Form submission handler
predictionForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Show loading
    showLoading();
    
    // Collect form data
    const formData = {
        male_dob: document.getElementById('male_dob').value,
        male_tob: document.getElementById('male_tob').value,
        male_lat: document.getElementById('male_lat').value,
        male_lon: document.getElementById('male_lon').value,
        male_tz_offset: 5.5, // IST timezone offset
        female_dob: document.getElementById('female_dob').value,
        female_tob: document.getElementById('female_tob').value,
        female_lat: document.getElementById('female_lat').value,
        female_lon: document.getElementById('female_lon').value,
        female_tz_offset: 5.5 // IST timezone offset
    };
    
    try {
        // Get current language from URL
        const currentLang = window.location.pathname.includes('/tamil') ? 'ta' : 'en';
        
        // Send API request
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Language': currentLang
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            const currentLang = window.location.pathname.includes('/tamil') ? 'ta' : 'en';
            const errorMsg = currentLang === 'ta' ? 'பகுப்பாய்வின் போது பிழை ஏற்பட்டது.' : 'An error occurred during analysis.';
            showError(data.error || errorMsg);
        }
    } catch (error) {
        console.error('Error:', error);
        const currentLang = window.location.pathname.includes('/tamil') ? 'ta' : 'en';
        const errorMsg = currentLang === 'ta' ? 'வலையமைப்பு பிழை. உங்கள் இணைப்பை சரிபார்த்து மீண்டும் முயற்சிக்கவும்.' : 'Network error. Please check your connection and try again.';
        showError(errorMsg);
    }
});

// Show loading spinner
function showLoading() {
    loading.classList.remove('hidden');
    results.classList.add('hidden');
    
    // Smooth scroll to loading
    loading.scrollIntoView({ behavior: 'smooth' });
}

// Display results
function displayResults(data) {
    // Hide loading
    loading.classList.add('hidden');
    
    // Get current language for labels
    const currentLang = window.location.pathname.includes('/tamil') ? 'ta' : 'en';
    
    // Update summary cards with enhanced details
    document.getElementById('male-rahu-nakshatra').textContent = data.male_rahu_nakshatra;
    document.getElementById('rahu-lord').textContent = currentLang === 'ta' ? `ஆட்சியாளர்: ${data.rahu_nakshatra_lord}` : `Lord: ${data.rahu_nakshatra_lord}`;
    document.getElementById('rahu-details').textContent = currentLang === 'ta' ? `நிலை: ${data.male_rahu.longitude.toFixed(2)}° ${data.male_rahu.rasi}ல்` : `Position: ${data.male_rahu.longitude.toFixed(2)}° in ${data.male_rahu.rasi}`;
    
    document.getElementById('male-ketu-nakshatra').textContent = data.male_ketu_nakshatra;
    document.getElementById('ketu-lord').textContent = currentLang === 'ta' ? `ஆட்சியாளர்: ${data.ketu_nakshatra_lord}` : `Lord: ${data.ketu_nakshatra_lord}`;
    document.getElementById('ketu-details').textContent = currentLang === 'ta' ? `நிலை: ${data.male_ketu.longitude.toFixed(2)}° ${data.male_ketu.rasi}ல்` : `Position: ${data.male_ketu.longitude.toFixed(2)}° in ${data.male_ketu.rasi}`;
    
    document.getElementById('total-matches').textContent = data.total_matches;
    document.getElementById('match-type').textContent = currentLang === 'ta' ? `வகை: ${data.primary_match_type === 'Rahu' ? 'ராகு' : data.primary_match_type === 'Ketu' ? 'கேது' : 'பொருத்தம் இல்லை'}` : `Type: ${data.primary_match_type}`;
    document.getElementById('match-breakdown').textContent = currentLang === 'ta' ? `ராகு: ${data.rahu_matches.length}, கேது: ${data.ketu_matches.length}` : `Rahu: ${data.rahu_matches.length}, Ketu: ${data.ketu_matches.length}`;
    
    // Update verdict
    const verdictCard = document.getElementById('verdict-card');
    const verdictIcon = document.getElementById('verdict-icon');
    const verdictTitle = document.getElementById('verdict-title');
    const verdictMessage = document.getElementById('verdict-message');
    
    // Remove existing classes
    verdictCard.classList.remove('high', 'moderate', 'low');
    
    // Add appropriate class and update content
    verdictCard.classList.add(data.verdict_class);
    
    if (data.verdict_class === 'high') {
        verdictIcon.className = 'fas fa-heart';
        verdictTitle.textContent = data.verdict;
    } else if (data.verdict_class === 'moderate') {
        verdictIcon.className = 'fas fa-balance-scale';
        verdictTitle.textContent = data.verdict;
    } else {
        verdictIcon.className = 'fas fa-exclamation-triangle';
        verdictTitle.textContent = data.verdict;
    }
    
    verdictMessage.textContent = data.message;
    
    // Populate compatibility table
    populateCompatibilityTable(data.compatibility_data);
    
    // Populate reasoning boxes
    populateReasoningBoxes(data);
    
    // Show results
    results.classList.remove('hidden');
    
    // Smooth scroll to results
    setTimeout(() => {
        results.scrollIntoView({ behavior: 'smooth' });
    }, 100);
}

// Populate compatibility table
function populateCompatibilityTable(compatibilityData) {
    const tableBody = document.getElementById('compatibility-table-body');
    tableBody.innerHTML = '';
    
    compatibilityData.forEach(item => {
        const row = document.createElement('tr');
        row.className = item.status;
        
        const statusIcon = item.status === 'match' ? '✓' : '✗';
        const statusClass = item.status === 'match' ? 'match' : 'no-match';
        
        // Get current language for reasoning message
        const currentLang = window.location.pathname.includes('/tamil') ? 'ta' : 'en';
        const noMatchReasoning = currentLang === 'ta' ? 'பொருத்தம் கண்டறியப்படவில்லை' : 'No match found';
        
        row.innerHTML = `
            <td>${item.condition}</td>
            <td>${item.value}</td>
            <td>${item.match_type}</td>
            <td class="status ${statusClass}">${statusIcon}</td>
            <td><small>${item.reasoning || noMatchReasoning}</small></td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Populate reasoning boxes
function populateReasoningBoxes(data) {
    // Hide all reasoning boxes first
    document.getElementById('rahu-reasoning-box').classList.add('hidden');
    document.getElementById('ketu-reasoning-box').classList.add('hidden');
    document.getElementById('no-matches-box').classList.add('hidden');
    
    // Show and populate Rahu reasoning
    if (data.rahu_reasoning && data.rahu_reasoning.length > 0) {
        const rahuBox = document.getElementById('rahu-reasoning-box');
        const rahuContent = document.getElementById('rahu-reasoning-content');
        rahuContent.innerHTML = '';
        
        data.rahu_reasoning.forEach(reason => {
            const p = document.createElement('p');
            p.textContent = reason;
            rahuContent.appendChild(p);
        });
        
        rahuBox.classList.remove('hidden');
    }
    
    // Show and populate Ketu reasoning
    if (data.ketu_reasoning && data.ketu_reasoning.length > 0) {
        const ketuBox = document.getElementById('ketu-reasoning-box');
        const ketuContent = document.getElementById('ketu-reasoning-content');
        ketuContent.innerHTML = '';
        
        data.ketu_reasoning.forEach(reason => {
            const p = document.createElement('p');
            p.textContent = reason;
            ketuContent.appendChild(p);
        });
        
        ketuBox.classList.remove('hidden');
    }
    
    // Show no matches box if no matches found
    if ((!data.rahu_reasoning || data.rahu_reasoning.length === 0) && 
        (!data.ketu_reasoning || data.ketu_reasoning.length === 0)) {
        document.getElementById('no-matches-box').classList.remove('hidden');
    }
}

// Show error message
function showError(message) {
    loading.classList.add('hidden');
    
    // Create error alert
    const errorAlert = document.createElement('div');
    errorAlert.className = 'error-alert';
    errorAlert.innerHTML = `
        <div style="
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #f5c6cb;
            margin: 20px;
            text-align: center;
            font-weight: 500;
        ">
            <i class="fas fa-exclamation-circle"></i> ${message}
        </div>
    `;
    
    // Insert error after form
    const formContainer = document.querySelector('.form-container');
    formContainer.appendChild(errorAlert);
    
    // Remove error after 5 seconds
    setTimeout(() => {
        errorAlert.remove();
    }, 5000);
}

// Reset form
function resetForm() {
    predictionForm.reset();
    results.classList.add('hidden');
    loading.classList.add('hidden');
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Print results
function printResults() {
    const printWindow = window.open('', '_blank');
    const resultsContent = results.innerHTML;
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vedic Life Partner Prediction Results</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    line-height: 1.6;
                }
                .print-header {
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 20px;
                }
                .print-header h1 {
                    color: #667eea;
                    margin-bottom: 10px;
                }
                .summary-cards {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .summary-card {
                    border: 1px solid #ddd;
                    padding: 15px;
                    text-align: center;
                    border-radius: 10px;
                }
                .verdict-card {
                    border: 2px solid #667eea;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    background: #f8f9fa;
                }
                .compatibility-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                .compatibility-table th,
                .compatibility-table td {
                    border: 1px solid #ddd;
                    padding: 10px;
                    text-align: left;
                }
                .compatibility-table th {
                    background: #667eea;
                    color: white;
                }
                .match {
                    background: #d4edda;
                }
                .no-match {
                    background: #f8f9fa;
                }
                @media print {
                    .action-buttons {
                        display: none;
                    }
                }
            </style>
        </head>
        <body>
            <div class="print-header">
                <h1>🔮 Vedic Life Partner Prediction Results</h1>
                <p>Generated on ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}</p>
            </div>
            ${resultsContent}
        </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.print();
}

// Add form validation
function addFormValidation() {
    const inputs = predictionForm.querySelectorAll('input[required]');
    
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                validateField(this);
            }
        });
    });
}

// Validate individual field
function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    
    // Remove existing error styling
    field.classList.remove('error');
    
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Validation rules
    let isValid = true;
    let errorMessage = '';
    
    // Get current language
    const currentLang = window.location.pathname.includes('/tamil') ? 'ta' : 'en';
    
    if (!value) {
        isValid = false;
        errorMessage = currentLang === 'ta' ? 'இந்த புலம் தேவை.' : 'This field is required.';
    } else if (fieldName.includes('lat') || fieldName.includes('lon')) {
        const numValue = parseFloat(value);
        if (isNaN(numValue)) {
            isValid = false;
            errorMessage = currentLang === 'ta' ? 'சரியான எண்ணை உள்ளிடவும்.' : 'Please enter a valid number.';
        } else if (fieldName.includes('lat') && (numValue < -90 || numValue > 90)) {
            isValid = false;
            errorMessage = currentLang === 'ta' ? 'அட்சரேகை -90 முதல் 90 வரை இருக்க வேண்டும்.' : 'Latitude must be between -90 and 90.';
        } else if (fieldName.includes('lon') && (numValue < -180 || numValue > 180)) {
            isValid = false;
            errorMessage = currentLang === 'ta' ? 'தீர்க்கரேகை -180 முதல் 180 வரை இருக்க வேண்டும்.' : 'Longitude must be between -180 and 180.';
        }
    }
    
    // Apply error styling and message
    if (!isValid) {
        field.classList.add('error');
        field.style.borderColor = '#e74c3c';
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.color = '#e74c3c';
        errorDiv.style.fontSize = '0.8rem';
        errorDiv.style.marginTop = '5px';
        errorDiv.textContent = errorMessage;
        
        field.parentNode.appendChild(errorDiv);
    } else {
        field.style.borderColor = '#27ae60';
    }
    
    return isValid;
}

// Initialize form validation
document.addEventListener('DOMContentLoaded', function() {
    addFormValidation();
    
    // Add some sample data for testing
    const today = new Date();
    const sampleDate = new Date(today.getFullYear() - 25, today.getMonth(), today.getDate());
    
    // Set sample data (optional - for testing)
    if (window.location.search.includes('sample=true')) {
        document.getElementById('male_dob').value = '1978-09-18';
        document.getElementById('male_tob').value = '17:35';
        document.getElementById('male_lat').value = '13.08333333';
        document.getElementById('male_lon').value = '80.28333333';
        
        document.getElementById('female_dob').value = '1984-01-15';
        document.getElementById('female_tob').value = '13:30';
        document.getElementById('female_lat').value = '11.9416';
        document.getElementById('female_lon').value = '79.8083';
    }
});

// Add smooth animations for better UX
function addSmoothAnimations() {
    // Animate summary cards on load
    const summaryCards = document.querySelectorAll('.summary-card');
    summaryCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Call animation function when results are displayed
const originalDisplayResults = displayResults;
displayResults = function(data) {
    originalDisplayResults(data);
    setTimeout(addSmoothAnimations, 100);
};
