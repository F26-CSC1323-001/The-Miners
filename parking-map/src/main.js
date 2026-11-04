import './style.css' // get the style for the gui

const Total_Count = 8;

// Initially all the spaces are free
let parkingSpaces = Array(Total_Count).fill("free");

document.querySelector("#app").innerHTML = `
<header class="topbar">
  <div class="brand">
    <div class="brand-icon">P</div>
    <div>
      <h1>Smart Parking</h1>
      <p>Parking Management System</p>
    </div>
  </div>
  <div class="connection">
    <span class="connection-dot"></span>
    <span id="connection-text">Connecting...</span>
  </div>
</header>

<main class="dashboard">
  <section class="welcome">
    <div>
      <p class="eyebrow">PARKING OVERVIEW</p>
      <h2>Find your parking space</h2>
      <p class="subtitle">
        Monitor parking availability in real time
      </p>
    </div>
    <div class="total-badge">
      <span class="total-number" id="total-count">12</span>
      <span>Total spaces</span>
    </div>
  </section>

  <section class="stats">
    <article class="stat-card">
      <div class="stat-icon total-icon">P</div>
      <div>
        <p>Total Spaces</p>
        <strong id="total-stat">12</strong>
      </div>
    </article>

    <article class="stat-card">
      <div class="stat-icon free-icon">✓</div>
      <div>
        <p>Available</p>
        <strong id="free-count">12</strong>
      </div>
    </article>

    <article class="stat-card">
      <div class="stat-icon occupied-icon">●</div>
      <div>
        <p>Occupied</p>
        <strong id="occupied-count">0</strong>
      </div>
    </article>
  </section>

  <section class="parking-panel">
    <div class="panel-heading">
      <div>
        <h3>Parking Map</h3>
        <p>Select a space to see its status</p>
      </div>
      <div class="legend">
        <span><i class="legend-dot free-dot"></i> Available</span>
        <span><i class="legend-dot occupied-dot"></i> Occupied</span>
      </div>
    </div>

    <div class="parking-entrance">
      <span>ENTRANCE</span>
      <!-- Need to finish -->
    </div>

    <div id="parking-map" class="parking-map"></div>

    <div class="selected-space" id="selected-space" aria-live="polite">
      Select a parking space to view status
    </div>

    <div class="panel-footer">
      <span id="availability-message"></span>
    <!-- get rid of samble button
      <button id="simulate-button" type="button">
        Simulate update
      </button> -->
    </div>
  </section>

  <p class="page-note">
    Smart Parking Dashboard - Demo Interface
  </p>
</main>
`;

// GUI created by Silvia:
const parkingMap = document.querySelector("#parking-map");
const selectedSpace = document.querySelector("#selected-space");

function renderParkingMap() {
  parkingMap.innerHTML = parkingSpaces.map((status, index) => {
    const number = String(index + 1).padStart(2, "0");
    const isFree = status === "free";
    return `
      <button
        type="button"
        class="parking-space ${isFree ? 'free' : 'occupied'}"
        data-index="${index}"
        aria-label="Parking space P${number}: ${isFree ? 'Available' : 'Occupied'}"
      >
        <span class="space-number">P${number}</span>
        <span class="space-symbol">${isFree ? '✓' : '●'}</span>
        <span class="space-status">${isFree ? 'Available' : 'Occupied'}</span>
      </button>
    `;
  }).join("");
}

function updateCounters() {
  const free = parkingSpaces.filter(status => status === "free").length;
  const occupied = parkingSpaces.filter(status => status === "occupied").length;

  document.querySelector("#total-count").textContent = parkingSpaces.length;
  document.querySelector("#total-stat").textContent = parkingSpaces.length;
  document.querySelector("#free-count").textContent = free;
  document.querySelector("#occupied-count").textContent = occupied;

  document.querySelector("#availability-message").textContent =
    `${free} of ${parkingSpaces.length} spaces available`;
}

// Function to update the GUI with data from another part of the project
function updateParkingGUI(statuses) {

  if (!Array.isArray(statuses) || statuses.length === 0) {
  console.error("Expected a non-empty array of parking statuses");
  return;
  }

  if (!statuses.every(status => status === "free" || status === "occupied")) {
    console.error('Each status must be "free" or "occupied".');
    return;
  }
  parkingSpaces = [...statuses];
  renderParkingMap();
  updateCounters();
}

parkingMap.addEventListener("click", event => {
  const space = event.target.closest(".parking-space");
  if (!space) return;

  const index = Number(space.dataset.index);
  const status = parkingSpaces[index];
  const number = String(index + 1).padStart(2, "0");

  selectedSpace.textContent =
    `Parking space P${number} is ${status === "free" ? "available" : "occupied"}.`;
});

/* // simulate update button is no longer needed
document.querySelector("#simulate-button").addEventListener("click", () => {
  // Demo only: simulate a new parking status
  const nextStatuses = parkingSpaces.map(() => Math.random() < 0.3 ? "occupied" : "free");
  updateParkingGUI(nextStatuses);
  selectedSpace.textContent = "Parking information updated successfully (demo).";
});
*/
// End of GUI

// Make the function accessible to other JavaScript modules
window.updateParkingGUI = updateParkingGUI;

renderParkingMap();
updateCounters();

/*
// Backend address: comes from .env (VITE_API_URL), falls back to local Flask
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";
console.log(API_URL);
document.getElementById("camera").src = `${API_URL}/api/video`;
*/

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";
//const API_URL = "http://localhost:5000";
const cam = document.getElementById("camera");
let busy = false;

async function refreshCamera() {

  if (busy) return; // don't start a new request until the last one finishes
  busy = true;
  try {
    //const res = await fetch(`${API_URL}/api/frame`, {
    const res = await fetch(`${API_URL}/api/annotated`, {
      headers: { "ngrok-skip-browser-warning": "true" },
    });
    if (!res.ok) throw new Error("No frame yet");
    const blob = await res.blob();
    const old = cam.src;
    cam.src = URL.createObjectURL(blob);
    if (old.startsWith("blob:")) URL.revokeObjectURL(old);
  } catch (err) {
    console.error("Camera frame failed:", err);
  }
  busy = false;
}

// ---------- Live parking data from the Flask backend ----------
function setConnection(online) {
  document.querySelector("#connection-text").textContent =
    online ? "Live data" : "Backend offline";
}

async function fetchSpots() {
  try {
    const res = await fetch(`${API_URL}/api/spots`, {
      headers: { "ngrok-skip-browser-warning": "true" },
    });
    const data = await res.json(); // like {"spot1": "empty", "spot2": "occupied"}

    const statuses = Object.keys(data)
      .sort((a, b) => Number(a.replace("spot", "")) - Number(b.replace("spot", "")))
      .map(key => data[key]);
    if (statuses.length > 0) {
      updateParkingGUI(statuses);
    }
    setConnection(true);
  } catch (err) {
    console.error("Could not get spot data:", err);
    setConnection(false);
  }
}

const SPOTS_EVERY_MS = 7000;   // parking data: every 7 seconds
const CAMERA_EVERY_MS = 7000;  // camera picture: every 8 seconds

function every(ms, fn) {
  fn();                                      // run once right away
  setInterval(() => {
    if (!document.hidden) fn();              // skip while the tab isn't visible
  }, ms);
}

every(SPOTS_EVERY_MS, fetchSpots);
every(CAMERA_EVERY_MS, refreshCamera);