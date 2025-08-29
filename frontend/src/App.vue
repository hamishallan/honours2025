<template>
  <div class="app">
    <!-- Use SidebarMenu component -->
    <SidebarMenu />

    <!-- Main Content -->
    <main class="content"></main>
  </div>
</template>

<script setup>
import SidebarMenu from "@/components/SidebarMenu.vue";
</script>

<style scoped>
.app {
  display: flex;
  height: 100vh;
  width: 100vw;
}

.content {
  flex: 1;
  background-color: #f8fafc; /* slate-50 */
}
</style>
