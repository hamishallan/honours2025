<template>
  <div>
    <h1>Honours Soil Spectrum Visualisation</h1>
    <SpectrumSelector @selected="selectedSpectrum = $event" />
    <PredictionCard :spectrum="selectedSpectrum" />
    <SpectrumPlot :spectrum="selectedSpectrum" />
  </div>
</template>

<script setup>
import { ref } from "vue";
import SpectrumSelector from "./components/SpectrumSelector.vue";
import SpectrumPlot from "./components/SpectrumPlot.vue";
import PredictionCard from "./components/PredictionCard.vue";

const selectedSpectrum = ref(null);
</script>
