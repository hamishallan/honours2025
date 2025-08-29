<!-- <template>
  <Dashboard />
</template>

<script setup>
import Dashboard from "./components/Dashboard.vue";
import "./assets/base.css";
</script> -->


<template>
  <div>
    <h2>Device Geomap</h2>
    <GrafanaEmbed
        dashboardUid="29d03190-8e2f-4766-8b52-3c479d20adc9"
        dashboardSlug="honours-dashboard"
        refresh="30s"
        height="800"
        />
  </div>
</template>

<script>
import GrafanaEmbed from "./components/GrafanaEmbed.vue";

export default {
  components: {
    GrafanaEmbed
  }
};
</script>
