<template>
  <main class="main-content">
    <div v-if="!selectedSpectrum" class="placeholder">
      Select a spectrum
    </div>

    <div v-else class="content-grid">
      <!-- Header -->
      <div class="header">
        <h1 class="spectrum-title">{{ selectedSpectrum.device_id }}</h1>
        <ToggleSwitch
          :modelValue="showPlot"
          @update:modelValue="$emit('update:showPlot', $event)"
          label="Show Spectrum Plot"
        />
      </div>

      <!-- Prediction Card -->
      <div class="left-panel">
        <PredictionCard :spectrum="selectedSpectrum" />
      </div>

      <!-- Plot -->
      <div class="right-panel">
        <SpectrumPlot v-if="showPlot" :spectrum="selectedSpectrum" />
      </div>
    </div>
  </main>
</template>

<script setup>
import PredictionCard from "./PredictionCard.vue";
import ToggleSwitch from "./ToggleSwitch.vue";
import SpectrumPlot from "./SpectrumPlot.vue";

defineProps({
  selectedSpectrum: Object,
  showPlot: Boolean
});
defineEmits(["update:showPlot"]);
</script>

<style scoped>
.main-content {
  margin-left: var(--sidebar-width, 260px);
  flex: 1;
  padding: 1.5rem;
  height: 100vh; /* make sure it fills the viewport height */
  box-sizing: border-box;
  overflow: hidden; /* prevent page scroll */
  display: flex;
  flex-direction: column;
}

.placeholder {
  opacity: 0.6;
  text-align: center;
  margin: auto;
  font-size: 1.2rem;
}

.content-grid {
  display: grid;
  grid-template-rows: auto 1fr;
  grid-template-columns: 1fr 1fr;
  grid-template-areas:
    "header header"
    "left-panel right-panel";
  gap: 1rem;
  height: 100%;
}

.header {
  grid-area: header;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.left-panel {
  grid-area: left-panel;
  overflow: auto;
}

.right-panel {
  grid-area: right-panel;
  overflow: auto;
}

.spectrum-title {
  margin: 0;
  color: #00b4d8;
}
</style>
