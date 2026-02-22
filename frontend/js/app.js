// ===============================
// CONFIG
// ===============================
const API_BASE = "http://127.0.0.1:8000"; // Change if deployed

let currentSelectedLocation = null;

// ===============================
// INITIALIZE
// ===============================
document.addEventListener('DOMContentLoaded', () => {

    fetchLocations();

    // Refresh AI Advice
    document.getElementById('refresh-advice').addEventListener('click', () => {
        if (currentSelectedLocation) {
            fetchAIInsights(currentSelectedLocation);
        }
    });

    // ===============================
    // FETCH BY CITY
    // ===============================
    document.getElementById('btn-fetch-city').addEventListener('click', async () => {

        const cityName = document.getElementById('form-city-name').value.trim();
        if (!cityName) {
            alert('Please enter a city name.');
            return;
        }

        const btn = document.getElementById('btn-fetch-city');
        const original = btn.innerHTML;
        btn.innerHTML = '<i data-lucide="loader" class="animate-spin" size="18"></i>';
        lucide.createIcons();

        try {
            const resp = await fetch(`${API_BASE}/pollution/fetch-by-city/${encodeURIComponent(cityName)}`, {
                method: 'POST'
            });

            if (!resp.ok) throw await resp.json();

            const record = await resp.json();

            alert(`Data for ${cityName} fetched successfully!`);
            hideManagement();

            await fetchLocations();
            loadDashboard(record.location_id);
            document.getElementById('location-select').value = record.location_id;

        } catch (err) {
            alert(err.detail || "Failed to fetch city data.");
        } finally {
            btn.innerHTML = original;
            lucide.createIcons();
        }
    });

    // ===============================
    // REAL-TIME FETCH BY LOCATION ID
    // ===============================
    document.getElementById('btn-fetch-real').addEventListener('click', async () => {

        const locId = document.getElementById('form-loc-id').value;
        if (!locId) {
            alert('Please enter a Location ID.');
            return;
        }

        const btn = document.getElementById('btn-fetch-real');
        const original = btn.innerHTML;
        btn.innerHTML = '<i data-lucide="loader" class="animate-spin" size="18"></i> Fetching...';
        lucide.createIcons();

        try {
            const resp = await fetch(`${API_BASE}/pollution/fetch-real/${locId}`, {
                method: 'POST'
            });

            if (!resp.ok) throw await resp.json();

            alert("Real-time data fetched successfully!");
            hideManagement();
            loadDashboard(locId);

        } catch (err) {
            alert(err.detail || "Failed to fetch real-time data.");
        } finally {
            btn.innerHTML = original;
            lucide.createIcons();
        }
    });

});


// ===============================
// FETCH LOCATIONS
// ===============================
async function fetchLocations() {
    try {
        const resp = await fetch(`${API_BASE}/locations/`);
        if (!resp.ok) throw new Error("Failed to fetch locations");

        const data = await resp.json();
        const select = document.getElementById('location-select');

        // Clear previous options
        select.innerHTML = '<option value="">Select Location</option>';

        data.forEach(loc => {
            const opt = document.createElement('option');
            opt.value = loc.id;
            opt.textContent = `${loc.name}, ${loc.city}`;
            select.appendChild(opt);
        });

    } catch (e) {
        console.error("Location fetch error:", e);
    }
}


// ===============================
// LOAD DASHBOARD
// ===============================
async function loadDashboard(locationId) {

    if (!locationId) return;

    currentSelectedLocation = locationId;

    try {
        // 1️⃣ Pollution
        const resp = await fetch(`${API_BASE}/pollution/?location_id=${locationId}`);
        const records = await resp.json();

        if (records.length === 0) {
            resetDashboardView();
            return;
        }

        const latest = records[0];
        updateStatsView(latest);

        // 2️⃣ Weather Prediction (Single Call)
        const weatherResp = await fetch(`${API_BASE}/ai/predict_weather/${locationId}`, {
            method: 'POST'
        });

        const weather = await weatherResp.json();
        updateWeatherView(weather);

        // 3️⃣ AI Analysis + Advice
        fetchAIInsights(locationId);

    } catch (e) {
        console.error("Dashboard load error:", e);
    }
}


// ===============================
// UPDATE UI
// ===============================
function updateStatsView(data) {

    document.getElementById('latest-aqi').textContent = data.aqi;
    document.getElementById('aqi-status').textContent = getAQIDesc(data.aqi);

    document.getElementById('pm25-val').textContent = `${data.pm25} µg/m³`;
    document.getElementById('pm10-val').textContent = `${data.pm10} µg/m³`;

    document.getElementById('pm25-bar').style.width =
        `${Math.min((data.pm25 / 300) * 100, 100)}%`;

    document.getElementById('pm10-bar').style.width =
        `${Math.min((data.pm10 / 300) * 100, 100)}%`;
}


function updateWeatherView(data) {
    document.getElementById('predicted-temp').textContent =
        `${data.predicted_temp}°C`;
    document.getElementById('weather-condition').textContent =
        data.condition;
}


// ===============================
// AI INSIGHTS
// ===============================
async function fetchAIInsights(locationId) {

    const adviceBox = document.getElementById('ai-advice-content');
    const analysisBox = document.getElementById('genai-analysis-text');

    adviceBox.innerHTML =
        '<i data-lucide="loader" class="animate-spin" size="16"></i> AI is analyzing...';
    analysisBox.textContent = "Analyzing trends...";
    lucide.createIcons();

    try {
        const analysisResp = await fetch(`${API_BASE}/ai/analyze/${locationId}`);
        const analysisData = await analysisResp.json();

        analysisBox.textContent =
            analysisData.analysis.substring(0, 150) + "...";

        const adviceResp = await fetch(`${API_BASE}/ai/advice/${locationId}`);
        const adviceData = await adviceResp.json();

        adviceBox.innerHTML =
            adviceData.advice.replace(/\n/g, '<br>');

    } catch (e) {
        adviceBox.textContent =
            "AI services unavailable. Check Gemini API key.";
        analysisBox.textContent =
            "AI analysis currently unavailable.";
    }
}


// ===============================
// HELPERS
// ===============================
function getAQIDesc(aqi) {
    if (aqi <= 50) return "Healthy Air Quality";
    if (aqi <= 100) return "Moderate Air Quality";
    if (aqi <= 150) return "Unhealthy for Sensitive Groups";
    if (aqi <= 200) return "Unhealthy";
    if (aqi <= 300) return "Very Unhealthy";
    return "Hazardous Pollution Levels";
}


function resetDashboardView() {
    document.getElementById('latest-aqi').textContent = "--";
    document.getElementById('predicted-temp').textContent = "--°C";
    document.getElementById('ai-advice-content').textContent =
        "No data found. Add pollution record.";
}


// ===============================
// MODAL TOGGLE
// ===============================
function showManagement() {
    document.getElementById('modal').classList.remove('hidden');
}

function hideManagement() {
    document.getElementById('modal').classList.add('hidden');
}


