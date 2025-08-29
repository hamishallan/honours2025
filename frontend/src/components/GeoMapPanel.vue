<template>
  <div class="grafana-panel">
    <iframe
      src="http://localhost:3000/d-solo/your-dashboard-id?panelId=1"
      width="100%"
      height="100%"
      frameborder="0"
    ></iframe>
  </div>
</template>

<style scoped>
.grafana-panel {
  width: 100%;
  height: 100%;
}
</style>
