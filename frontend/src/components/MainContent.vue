<template>
  <main class="main-content">
    <div v-if="!selectedSpectrum" class="placeholder">Select a spectrum</div>

    <div v-else class="two-col">
      <div class="header">
        <h1 class="spectrum-title">Spectrum Dashboard</h1>
      </div>

      <!-- Left column: Prediction -->
      <div class="col pred">
        <PredictionCard :spectrum="selectedSpectrum" />
      </div>

      <!-- Right column: Plots -->
      <div class="col plots">
        <SpectrumPlot :spectrum="selectedSpectrum" />
      </div>
    </div>
  </main>
</template>

<script setup>
import PredictionCard from "./PredictionCard.vue";
import SpectrumPlot from "./SpectrumPlot.vue";

defineProps({
  selectedSpectrum: Object,
});
</script>

<style scoped>
.main-content {
  height: 100vh; /* fills the grid row */
  overflow: hidden; /* internal panels scroll, not the page */
  display: flex;
  flex-direction: column;
}

.placeholder {
  opacity: 0.6;
  text-align: center;
  margin: auto;
  font-size: 1.2rem;
}

.two-col {
  display: grid;
  grid-template-rows: auto 1fr; /* header + content */
  grid-template-columns: 360px 1fr; /* left (pred) | right (plots) */
  grid-template-areas:
    "header header"
    "pred   plots";
  gap: 1rem;
  height: 100%;
  min-width: 0; /* prevents overflow truncation */
}

.header {
  grid-area: header;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #22324b;
  padding: 0.5rem 0;
}

.spectrum-title {
  margin: 0;
  color: #f0f0f0;
}

.col.pred {
  grid-area: pred;
  overflow: auto; /* scroll only this panel if needed */
  padding: 1rem;
}

.col.plots {
  grid-area: plots;
  overflow: auto; /* scroll only this panel if needed */
  min-width: 0; /* lets charts shrink properly */
  padding: 1rem;
}

/* Responsive: stack on narrow screens */
@media (max-width: 1000px) {
  .two-col {
    grid-template-columns: 1fr;
    grid-template-areas:
      "header"
      "pred"
      "plots";
  }
}
</style>
