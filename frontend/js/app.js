const API_BASE = window.location.origin;

// State management
let currentSelectedLocation = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchLocations();

    // Refresh advice button
    document.getElementById('refresh-advice').addEventListener('click', () => {
        if (currentSelectedLocation) {
            fetchAIInsights(currentSelectedLocation);
        }
    });

    // Form submission
    document.getElementById('record-form').addEventListener('submit', async (e) => {
        // ... (manual submission code)
    });

    // Fetch by City button
    document.getElementById('btn-fetch-city').addEventListener('click', async () => {
        const cityName = document.getElementById('form-city-name').value;
        if (!cityName) {
            alert('Please enter a city name.');
            return;
        }

        const btn = document.getElementById('btn-fetch-city');
        const originalContent = btn.innerHTML;
        btn.innerHTML = '<i data-lucide="loader" class="animate-spin" size="18"></i>';
        lucide.createIcons();

        try {
            const resp = await fetch(`${API_BASE}/pollution/fetch-by-city/${encodeURIComponent(cityName)}`, { method: 'POST' });
            if (resp.ok) {
                const record = await resp.json();
                alert(`Data for ${cityName} fetched and saved successfully!`);
                hideManagement();

                // Refresh locations list just in case a new one was created
                document.getElementById('location-select').innerHTML = '<option value="" class="bg-slate-900">Select Location</option>';
                await fetchLocations();

                loadDashboard(record.location_id);
                document.getElementById('location-select').value = record.location_id;
            } else {
                const err = await resp.json();
                alert(`Error: ${err.detail || 'Failed to fetch data for city'}`);
            }
        } catch (e) {
            console.error(e);
            alert('Connection error.');
        } finally {
            btn.innerHTML = originalContent;
            lucide.createIcons();
        }
    });

    // Real-time fetch button
    document.getElementById('btn-fetch-real').addEventListener('click', async () => {
        const locId = document.getElementById('form-loc-id').value;
        if (!locId) {
            alert('Please enter a Location ID first.');
            return;
        }

        const btn = document.getElementById('btn-fetch-real');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i data-lucide="loader" class="animate-spin" size="18"></i> Fetching...';
        lucide.createIcons();

        try {
            // Updated endpoint name
            const resp = await fetch(`${API_BASE}/pollution/fetch-by-city/${locId}`, { method: 'POST' });
            if (resp.ok) {
                alert('Real-time data fetched and saved successfully!');
                hideManagement();
                loadDashboard(locId);
            } else {
                const err = await resp.json();
                alert(`Error: ${err.detail || 'Failed to fetch real-time data'}`);
            }
        } catch (e) {
            console.error(e);
            alert('Connection error. Is the server running?');
        } finally {
            btn.innerHTML = originalText;
            lucide.createIcons();
        }
    });
});

async function fetchLocations() {
    try {
        const resp = await fetch(`${API_BASE}/locations/`);
        const data = await resp.json();
        const select = document.getElementById('location-select');

        data.forEach(loc => {
            const opt = document.createElement('option');
            opt.value = loc.id;
            opt.textContent = `${loc.name}, ${loc.city}`;
            opt.className = 'bg-slate-900';
            select.appendChild(opt);
        });

        // Add dummy location if none exist
        if (data.length === 0) {
            // Seed a location via API for demo
            await fetch(`${API_BASE}/locations/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: "Central Park",
                    city: "New York",
                    country: "USA",
                    latitude: 40.785091,
                    longitude: -73.968285
                })
            });
            fetchLocations(); // Refresh
        }
    } catch (e) {
        console.error("Failed to fetch locations", e);
    }
}

async function loadDashboard(locationId) {
    if (!locationId) return;
    currentSelectedLocation = locationId;

    // 1. Fetch Latest Pollution Record
    try {
        const resp = await fetch(`${API_BASE}/pollution/?location_id=${locationId}`);
        const records = await resp.json();

        if (records.length > 0) {
            const latest = records[0];
            updateStatsView(latest);

            // 2. Trigger Weather Prediction
            await fetch(`${API_BASE}/ai/predict_weather/${locationId}`, { method: 'POST' });
            const weatherResp = await fetch(`${API_BASE}/ai/predict_weather/${locationId}`, { method: 'POST' });
            const weather = await weatherResp.json();
            updateWeatherView(weather);

            // 3. Fetch AI Insights (Analyze + Advice)
            fetchAIInsights(locationId);
        } else {
            resetDashboardView();
        }
    } catch (e) {
        console.error("Failed to load dashboard data", e);
    }
}

function updateStatsView(data) {
    document.getElementById('latest-aqi').textContent = data.aqi;
    document.getElementById('aqi-status').textContent = getAQIDesc(data.aqi);

    // Pollutant Bars
    document.getElementById('pm25-val').textContent = `${data.pm25} µg/m³`;
    document.getElementById('pm10-val').textContent = `${data.pm10} µg/m³`;

    // Max values for bars (assumed 300)
    document.getElementById('pm25-bar').style.width = `${Math.min((data.pm25 / 300) * 100, 100)}%`;
    document.getElementById('pm10-bar').style.width = `${Math.min((data.pm10 / 300) * 100, 100)}%`;
}

function updateWeatherView(data) {
    document.getElementById('predicted-temp').textContent = `${data.predicted_temp}°C`;
    document.getElementById('weather-condition').textContent = data.condition;
}

async function fetchAIInsights(locationId) {
    const adviceBox = document.getElementById('ai-advice-content');
    const analysisBox = document.getElementById('genai-analysis-text');

    adviceBox.innerHTML = '<div class="flex items-center gap-2"><i data-lucide="loader" class="animate-spin" size="16"></i> AI is thinking...</div>';
    analysisBox.textContent = 'Analyzing trends...';
    lucide.createIcons();

    try {
        // Analysis
        const analysisResp = await fetch(`${API_BASE}/ai/analyze/${locationId}`);
        const analysisData = await analysisResp.json();
        analysisBox.textContent = analysisData.analysis.substring(0, 150) + "...";

        // Advice
        const adviceResp = await fetch(`${API_BASE}/ai/advice/${locationId}`);
        const adviceData = await adviceResp.json();
        adviceBox.innerHTML = adviceData.advice.replace(/\n/g, '<br>');
    } catch (e) {
        adviceBox.textContent = "Please set your Gemini API key to enable AI features.";
        analysisBox.textContent = "AI analysis currently unavailable.";
    }
}

function getAQIDesc(aqi) {
    if (aqi <= 50) return "Healthy Air Quality";
    if (aqi <= 100) return "Moderate Air Quality";
    if (aqi <= 150) return "Unhealthy for Sensitive Groups";
    return "Hazardous Pollution Levels";
}

function resetDashboardView() {
    document.getElementById('latest-aqi').textContent = "--";
    document.getElementById('predicted-temp').textContent = "--°C";
    document.getElementById('ai-advice-content').textContent = "No data found for this location. Add a record to begin.";
}

// Modal Toggle
function showManagement() { document.getElementById('modal').classList.remove('hidden'); }
function hideManagement() { document.getElementById('modal').classList.add('hidden'); }
