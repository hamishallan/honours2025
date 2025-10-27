<template>
  <div id="app">
    <h1 class="title">Raspberry Pi Control Panel</h1>
    <p class="subtitle">Remotely start your Pi integration script with one click.</p>
    <button @click="startPi" class="btn">Start Raspberry Pi Script</button>
    <p class="footer">© 2025 In-Situ Soil Monitoring Project</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: "hamish",
      password: "hamanator",
      apiBase: "https://rekehtm1f0.execute-api.us-east-1.amazonaws.com/dev/",
      accessToken: null,
      refreshToken: null,
      accessExpiry: null,
    };
  },

  methods: {
    // === 🔐 Authentication ===
    async getToken() {
      console.log("🔑 Requesting new token pair...");
      const res = await fetch(`${this.apiBase}token/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: this.username,
          password: this.password,
        }),
      });

      if (!res.ok) throw new Error("Failed to get token");
      const data = await res.json();
      this.accessToken = data.access;
      this.refreshToken = data.refresh;
      this.accessExpiry = new Date(Date.now() + 55 * 60 * 1000);
      console.log("✅ Token acquired");
    },

    async refreshTokenPair() {
      console.log("♻️ Refreshing token...");
      const res = await fetch(`${this.apiBase}token/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh: this.refreshToken }),
      });

      if (!res.ok) {
        console.warn("Refresh failed — getting new token pair");
        await this.getToken();
        return;
      }

      const data = await res.json();
      this.accessToken = data.access;
      this.accessExpiry = new Date(Date.now() + 55 * 60 * 1000);
      console.log("✅ Token refreshed");
    },

    async ensureTokenValid() {
      if (!this.accessToken || new Date() >= this.accessExpiry) {
        try {
          await this.refreshTokenPair();
        } catch (err) {
          console.warn("Refresh failed, fetching new token:", err);
          await this.getToken();
        }
      }
    },

    // === 🚀 Command to start Pi ===
    async startPi() {
        try {
            await this.ensureTokenValid();

            const payload = { device_id: "pi-001", command: "start" };

            const response = await fetch(`${this.apiBase}start-pi-script/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${this.accessToken}`,
            },
            body: JSON.stringify(payload),
            });

            if (!response.ok) {
            const errText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errText}`);
            }

            const data = await response.json();
            console.log("✅ Response:", data);
            alert("Command sent to Raspberry Pi!");
        } catch (error) {
            console.error("❌ Failed to trigger Pi:", error);
            alert("Error sending command.");
        }
    }


  },

  // Automatically log in once the page loads
  async mounted() {
    await this.getToken();
  },
};
</script>

<style>
.btn {
  background-color: #1976d2;
  color: white;
  padding: 10px 18px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.btn:hover {
  background-color: #125ea8;
}
</style>
