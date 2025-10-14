// CarbonSaver JavaScript

let carbonChart = null;

// API Base URL
const API_BASE = window.location.origin;

// Form submission handler
document.getElementById('optimizeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form values
    const powerKw = parseFloat(document.getElementById('powerKw').value);
    const durationHours = parseInt(document.getElementById('durationHours').value);
    const standardStartHour = parseInt(document.getElementById('standardStartHour').value);
    
    // Validate inputs
    if (powerKw <= 0 || durationHours <= 0 || standardStartHour < 0 || standardStartHour > 23) {
        showError('Please enter valid values for all fields');
        return;
    }
    
    // Show loading state
    setLoading(true);
    hideError();
    hideResults();
    
    try {
        // Call the API
        const response = await fetch(`${API_BASE}/api/optimize-forecast`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                power_kw: powerKw,
                duration_hours: durationHours,
                standard_start_hour: standardStartHour
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to fetch optimization');
        }
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            throw new Error('Optimization failed');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to optimize load profile. Please try again.');
    } finally {
        setLoading(false);
    }
});

function setLoading(loading) {
    const btn = document.getElementById('optimizeBtn');
    const btnText = btn.querySelector('.btn-text');
    const spinner = btn.querySelector('.spinner');
    
    btn.disabled = loading;
    
    if (loading) {
        btnText.textContent = 'Optimizing...';
        spinner.style.display = 'inline-block';
    } else {
        btnText.textContent = 'Get Forecast & Optimize';
        spinner.style.display = 'none';
    }
}

function displayResults(data) {
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
    
    // Update date info
    document.getElementById('dateInfo').textContent = `Forecast Date: ${data.date}`;
    
    // Update standard profile
    document.getElementById('standardStartTime').textContent = data.standard_profile.start_time;
    document.getElementById('standardEndTime').textContent = data.standard_profile.end_time;
    document.getElementById('standardEnergy').textContent = `${data.standard_profile.energy_kwh.toFixed(0)} kWh`;
    document.getElementById('standardIntensity').textContent = `${data.standard_profile.avg_carbon_intensity.toFixed(2)} g/kWh`;
    document.getElementById('standardEmissions').textContent = `${data.standard_profile.total_emissions_kg.toFixed(2)} kg CO₂`;
    
    // Update optimal profile
    document.getElementById('optimalStartTime').textContent = data.optimal_profile.start_time;
    document.getElementById('optimalEndTime').textContent = data.optimal_profile.end_time;
    document.getElementById('optimalEnergy').textContent = `${data.optimal_profile.energy_kwh.toFixed(0)} kWh`;
    document.getElementById('optimalIntensity').textContent = `${data.optimal_profile.avg_carbon_intensity.toFixed(2)} g/kWh`;
    document.getElementById('optimalEmissions').textContent = `${data.optimal_profile.total_emissions_kg.toFixed(2)} kg CO₂`;
    
    // Update savings
    const savings = data.savings;
    document.getElementById('savingsAmount').textContent = `${savings.emissions_saved_kg.toFixed(2)} kg CO₂`;
    document.getElementById('savingsPct').textContent = `${savings.emissions_saved_pct.toFixed(1)}%`;
    document.getElementById('timeShift').textContent = `${savings.time_shift_hours >= 0 ? '+' : ''}${savings.time_shift_hours.toFixed(0)} hours`;
    document.getElementById('kmEquivalent').textContent = `${savings.km_equivalent.toFixed(0)} km`;
    
    // Update recommendation
    const recommendation = document.getElementById('recommendation');
    if (savings.emissions_saved_kg > 1) {
        recommendation.innerHTML = `
            <strong>💡 Recommendation:</strong> Shift your load to start at 
            <strong>${data.optimal_profile.start_time}</strong> to save 
            <strong>${savings.emissions_saved_kg.toFixed(2)} kg CO₂</strong>! 
            That's equivalent to avoiding <strong>${savings.km_equivalent.toFixed(0)} km</strong> of driving.
        `;
    } else {
        recommendation.innerHTML = `
            <strong>✓ Your standard schedule is already near-optimal!</strong> 
            There's minimal opportunity for emission reduction through time-shifting.
        `;
    }
    
    // Update chart
    updateChart(data.hourly_data);
    
    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function updateChart(hourlyData) {
    const ctx = document.getElementById('carbonChart').getContext('2d');
    
    // Prepare data for chart
    const labels = hourlyData.map(d => `${d.hour.toString().padStart(2, '0')}:00`);
    const carbonIntensity = hourlyData.map(d => d.carbon_intensity);
    
    // Create background colors (highlight optimal and standard windows)
    const backgroundColors = hourlyData.map(d => {
        if (d.is_optimal_window) {
            return 'rgba(75, 192, 192, 0.8)'; // Green for optimal
        } else if (d.is_standard_window) {
            return 'rgba(255, 206, 86, 0.8)'; // Yellow for standard
        } else {
            return 'rgba(54, 162, 235, 0.6)'; // Blue for others
        }
    });
    
    const borderColors = hourlyData.map(d => {
        if (d.is_optimal_window) {
            return 'rgba(75, 192, 192, 1)';
        } else if (d.is_standard_window) {
            return 'rgba(255, 206, 86, 1)';
        } else {
            return 'rgba(54, 162, 235, 1)';
        }
    });
    
    // Destroy existing chart if it exists
    if (carbonChart) {
        carbonChart.destroy();
    }
    
    // Create new chart
    carbonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Carbon Intensity (gCO₂/kWh)',
                data: carbonIntensity,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.parsed.y.toFixed(2);
                            
                            const dataIndex = context.dataIndex;
                            const point = hourlyData[dataIndex];
                            
                            if (point.is_optimal_window) {
                                label += ' (Optimal Window)';
                            } else if (point.is_standard_window) {
                                label += ' (Standard Window)';
                            }
                            
                            return label;
                        },
                        afterLabel: function(context) {
                            const dataIndex = context.dataIndex;
                            const point = hourlyData[dataIndex];
                            
                            return [
                                `Total Load: ${point.total_load_mw.toFixed(0)} MW`,
                                `Wind: ${point.wind_mw.toFixed(0)} MW`,
                                `Solar: ${point.solar_mw.toFixed(0)} MW`
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Carbon Intensity (gCO₂/kWh)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Hour of Day'
                    }
                }
            }
        }
    });
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorSection').style.display = 'block';
    document.getElementById('errorSection').scrollIntoView({ behavior: 'smooth' });
}

function hideError() {
    document.getElementById('errorSection').style.display = 'none';
}

function hideResults() {
    document.getElementById('resultsSection').style.display = 'none';
}

// Health check on page load
window.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        if (!response.ok) {
            console.warn('API health check failed');
        }
    } catch (error) {
        console.error('Failed to connect to API:', error);
    }
});
