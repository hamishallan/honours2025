<template>
  <div>
    <h1>Soil Spectrum Visualisation</h1>
    <SpectrumSelector @selected="selectedSpectrum = $event" />
    <SpectrumPlot :spectrum="selectedSpectrum" />
  </div>
</template>

<script setup>
import { ref } from "vue";
import SpectrumSelector from "./components/SpectrumSelector.vue";
import SpectrumPlot from "./components/SpectrumPlot.vue";

const selectedSpectrum = ref(null);
</script>
