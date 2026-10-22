import './style.css'

const Total_Count = 12

// initially all the spaces are empty
let ParkingSpaces = ["free", "free", "free", "free", "Free", "free", "free", "free", "free", "free", "free", "free"]

document.querySelector('#app').innerHTML = '
<header class="topbar">
<div class="brand">
<div calss="brand-icon">P</div>
<div>
<h1>Smart Parking</h1>
<p>Parking Management System</p>
</div>
</div>
<div class="Connection">
<span class="connection-dot"></span>
GUI Demo mode 
</div>
</header>

<main class="dashboard">
<section class="welcome>
<div>
<p class="eyebrow">PARKING OVERVIEW</p>
<h2>Find your parking space</h2>
<p class="subtitle">
Monitor parking availability in real time
</p>
</div>
<div calss="total-badge">
<span class="total-number" id="total-count">12</span>
<span>Total spaces</span>
</div>
</section>

<section class="stats">
<articel class="stat-card">
<div calss="stat-icon total-icon">P</div>
<div>
<p>Total Spaces</p>
<strong id="total-stat">12</strong>
</div>
</articel>

<article class="stat-card">
<div class="stat-icon occupied-icon">.</div>
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
<span><i class="legend-dot occupied-dot"></i> Occupiued</span>
</div>
</div>

<div class="parking-entrance">
<span>ENTRANCE</span>
<span></span> # Need to finish
</div>

<div id="parking-map" class="parking-mmap"></div>

<div class="selected-space" id="selected-space" aria-live="polite">
Select a parking space to view status
</div>

<div  class="panel-footer">
<span id="availability-message"></span>
<button id="simulate-button"type="button">
Simulate update
</button>
</div>
</section>

<p class="page-note">
Smart Parking Dashboard - Demo Interface
</p>
</main>'

const parkingMap= document.querySelector("#parking-Map")

const selectedSpace = document.querySelector("#selected-space")

function renderParkingMap() {parkingMap.innerHTML = parkingSapces.map((status, index) => {
    const number = String(index + 1).padStart(2, "0") 
    const isFree = status === "free"
    return '
    <button
    type="button"
    class="parking-space ${is Free ? 'free' : 'occupied'}"
    data-index="${index"}"
    aria-label=Parking space P${number}: ${isFree ? ?Availabel' : 'Occupied'}" 
    >
    <span class="space-number">P${number}</span>
    <span class="space-symbol">${isFree ? '✓' :  '●'}</span>
    <span class="space-status">${isFree ? 'Available': 'Occupied'}</span>
    </button>
    '
    )}.join(")
    }


function updateCounters() {
    const free = parkingSapces.filter(status => status === "free").length
    const occupied = ParkingSpaces.filter(status => status === "occupied").length

    document.querySelector("#total_count").textContent = parkingSpaces.length
    document.querySelector("#total-stat").textContent = parkingSpaces.length
    document.querySelector("#free-count").textContent = free
    document.querySelector("#occupied-count").textContent = occupied

    document.querySelector("#availability-message").textContent = "${free} of ${parkingSpaces.length} spaces available"
}

// Function to update GUI with data from another part of the project
function updateParkingGUI(statuses) {if (!Array.isArray(statuses) || statuses.length != Total_Count) {console.error("Expected an array of $Total_Count} parking statuses") 
    return}
    if (!statuses.every(status => status === "free" || status === "occupied")){
        console.error("Each status must be "free" or "ocuppied"." )
        return
    }
    parkinSpaces = [...statuses]
    renderParkingMap()
    updateCounters()}

parkingMap.addEventListener("click", event => {
    const space = event.target.closet(".parking-space")
    if (!space) return

    const index = Number(space.dateset.index)
    const status = parkingSpaces[index]
    const number = String(index + 1).padStart(2, "0")

    selectedSpace.textContent = "parking space P${number} is ${status === "free" ? "available" : "ocuppied"}."
})

    document.querySelector("#simulate-button").addEventListener("click", () => {
        // Demo only: simulate a new parking status
        const nextStatuses = parkingSapces.map(( => Math.random( < 0.3 ? "ocuppied" : "free")))
    updateParkingGUI(nextStatuses)
    selectedSpace.textContent = "parking information updated successfully (demo)."
    })

    // Make the function accessible t oother JavaScript modules.
    window.updateParkingGUI = updateParkingGUI

    renderParkingMap()
    updateCounters()
