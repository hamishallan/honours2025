<template>
  <div class="dashboard">
    <!-- Sidebar -->
    <aside class="sidebar">
      <h2>Available Spectra</h2>

      <!-- Show spinner while loading -->
      <div v-if="loading" class="spinner-container">
        <div class="spinner"></div>
        <span>Loading...</span>
      </div>

      <!-- Show spectra list when loaded -->
      <ul v-else class="spectrum-list">
        <li
          v-for="spectrum in spectra"
          :key="spectrum.id"
          :class="{ active: spectrum.id === selectedSpectrum?.id }"
          @click="selectSpectrum(spectrum)"
        >
          {{ spectrum.device_id }}
        </li>
      </ul>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <h1 v-if="!selectedSpectrum" class="placeholder">Select a spectrum</h1>

      <div v-else>
        <h1 class="spectrum-title">Spectrum: {{ selectedSpectrum.device_id }}</h1>
        <PredictionCard :spectrum="selectedSpectrum" />
        <ToggleSwitch v-model="showPlot" label="Show Spectrum Plot" />
        <SpectrumPlot v-if="showPlot" :spectrum="selectedSpectrum" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import SpectrumPlot from "./SpectrumPlot.vue";
import PredictionCard from "./PredictionCard.vue";
import ToggleSwitch from "./ToggleSwitch.vue";

const spectra = ref([]);
const selectedSpectrum = ref(null);
const showPlot = ref(false);
const loading = ref(true);

async function fetchSpectra() {
  loading.value = true;
  try {
    const res = await fetch("https://rekehtm1f0.execute-api.us-east-1.amazonaws.com/dev/spectra/"); // replace with your real endpoint
    spectra.value = await res.json();
  } catch (err) {
    console.error("Failed to load spectra", err);
  } finally {
    loading.value = false;
  }
}

function selectSpectrum(spectrum) {
  selectedSpectrum.value = spectrum;
}

onMounted(fetchSpectra);
</script>

<style scoped>
.dashboard {
  display: flex;
  height: 100vh;
  background-color: #0d1b2a;
  color: #e0e1dd;
  font-family: 'Inter', sans-serif;
}

/* Sidebar */
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 260px;
  height: 100vh;
  background: linear-gradient(180deg, #1b263b, #0d1b2a);
  padding: 1.5rem 1rem;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  overflow-y: auto;
}

.sidebar h2 {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Spinner styles */
.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 2rem;
  color: #a9bcd0;
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top: 4px solid #00b4d8;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  animation: spin 1s linear infinite;
  margin-bottom: 0.5rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.spectrum-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.spectrum-list li {
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.spectrum-list li:hover {
  background-color: #415a77;
}

.spectrum-list li.active {
  background-color: #00b4d8;
  color: #0d1b2a;
  font-weight: bold;
}

.main-content {
  margin-left: 260px;
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.placeholder {
  opacity: 0.6;
  text-align: center;
  margin-top: 2rem;
}

.spectrum-title {
  margin-bottom: 1.5rem;
  color: #00b4d8;
}
</style>
