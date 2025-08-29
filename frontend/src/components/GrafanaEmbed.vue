<template>
  <div class="grafana-embed">
    <iframe
      :src="computedUrl"
      :width="width"
      :height="height"
      frameborder="0"
      allowfullscreen
    ></iframe>
  </div>
</template>

<script>
export default {
  name: "GrafanaEmbed",
  props: {
    // Grafana base URL
    baseUrl: {
      type: String,
      default: "http://localhost:3000"
    },
    // Dashboard UID (from Grafana URL: /d/<UID>/...)
    dashboardUid: {
      type: String,
      required: true
    },
    // Optional: name slug (just for nicer URLs)
    dashboardSlug: {
      type: String,
      default: "dashboard"
    },
    // Panel ID if embedding a single panel
    panelId: {
      type: [String, Number],
      default: null
    },
    // Org ID in Grafana (usually 1)
    orgId: {
      type: [String, Number],
      default: 1
    },
    // Time range (Grafana expects "now-6h", "now", etc.)
    from: {
      type: String,
      default: "now-6h"
    },
    to: {
      type: String,
      default: "now"
    },
    refresh: {
      type: String,
      default: "10s"
    },
    width: {
      type: String,
      default: "100%"
    },
    height: {
      type: String,
      default: "600"
    }
  },
  computed: {
    computedUrl() {
      // Base URL
      let url;
      if (this.panelId) {
        // Single panel embed
        url = `${this.baseUrl}/d-solo/${this.dashboardUid}/${this.dashboardSlug}?orgId=${this.orgId}&refresh=${this.refresh}&from=${this.from}&to=${this.to}&panelId=${this.panelId}`;
      } else {
        // Full dashboard embed
        url = `${this.baseUrl}/d/${this.dashboardUid}/${this.dashboardSlug}?orgId=${this.orgId}&refresh=${this.refresh}&from=${this.from}&to=${this.to}`;
      }
      return url;
    }
  }
};
</script>

<style scoped>
.grafana-embed {
  display: flex;
  justify-content: center;
  align-items: center;
}
.grafana-embed iframe {
  border: none;
  border-radius: 8px;
}
</style>
