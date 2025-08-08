<template>
  <main class="main-content">
    <h1 v-if="!selectedSpectrum" class="placeholder">Select a spectrum</h1>

    <div v-else>
      <h1 class="spectrum-title">Spectrum: {{ selectedSpectrum.device_id }}</h1>
      <PredictionCard :spectrum="selectedSpectrum" />

      <!-- Bind the prop and emit updates -->
      <ToggleSwitch
        :modelValue="showPlot"
        @update:modelValue="$emit('update:showPlot', $event)"
        label="Show Spectrum Plot"
      />

      <SpectrumPlot v-if="showPlot" :spectrum="selectedSpectrum" />
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
