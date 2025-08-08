<template>
  <div>
    <h1>Honours Soil Spectrum Visualisation</h1>

    <SpectrumSelector @selected="selectedSpectrum = $event" />
    <PredictionCard :spectrum="selectedSpectrum" />

    <ToggleSwitch v-if="selectedSpectrum" v-model="showPlot" label="Show Spectrum Plot" />

    <SpectrumPlot v-if="showPlot" :spectrum="selectedSpectrum" />
  </div>
</template>

<script setup>
import { ref } from "vue";
import SpectrumSelector from "./components/SpectrumSelector.vue";
import SpectrumPlot from "./components/SpectrumPlot.vue";
import PredictionCard from "./components/PredictionCard.vue";
import ToggleSwitch from "./components/ToggleSwitch.vue";

const selectedSpectrum = ref(null);
const showPlot = ref(false);
</script>
