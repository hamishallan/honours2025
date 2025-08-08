<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>Honours Soil Spectrum Visualisation</h1>
    </header>

    <section class="dashboard-controls">
      <SpectrumSelector @selected="selectedSpectrum = $event" />
      <PredictionCard :spectrum="selectedSpectrum" />
      <ToggleSwitch
        v-if="selectedSpectrum"
        v-model="showPlot"
        label="Show Spectrum Plot"
      />
    </section>

    <section class="dashboard-main">
      <SpectrumPlot v-if="showPlot" :spectrum="selectedSpectrum" />
    </section>
  </div>
</template>

<script setup>
import { ref } from "vue";
import SpectrumSelector from "./SpectrumSelector.vue";
import SpectrumPlot from "./SpectrumPlot.vue";
import PredictionCard from "./PredictionCard.vue";
import ToggleSwitch from "./ToggleSwitch.vue";

const selectedSpectrum = ref(null);
const showPlot = ref(false);
</script>

<style scoped>
.dashboard {
  display: grid;
  grid-template-rows: auto auto 1fr;
  gap: 1.5rem;
  padding: 1rem;
  background-color: #1e293b;
  color: #f8fafc;
  min-height: 100vh;
}

.dashboard-header {
  text-align: center;
}

.dashboard-controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  align-items: start;
  background-color: #334155;
  padding: 1rem;
  border-radius: 8px;
}

.dashboard-main {
  background-color: #0f172a;
  padding: 1rem;
  border-radius: 8px;
}
</style>
