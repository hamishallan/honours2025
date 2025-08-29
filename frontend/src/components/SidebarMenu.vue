<template>
  <aside :class="['sidebar', { collapsed }]">
    <!-- Sidebar Header -->
    <div class="sidebar-header">
      <h2 v-show="!collapsed" class="sidebar-title">My App</h2>
      <button class="toggle-btn" @click="collapsed = !collapsed">
        <ChevronLeft v-if="!collapsed" class="chevron" />
        <ChevronRight v-else class="chevron" />
      </button>
    </div>

    <!-- Menu -->
    <nav>
      <ul>
        <li>
          <a href="#">
            <Home class="icon" />
            <span class="label" v-show="!collapsed">Home</span>
          </a>
        </li>
        <li>
          <a href="#">
            <BarChart class="icon" />
            <span class="label" v-show="!collapsed">Dashboard</span>
          </a>
        </li>
        <li>
          <a href="#">
            <Settings class="icon" />
            <span class="label" v-show="!collapsed">Settings</span>
          </a>
        </li>
      </ul>
    </nav>
  </aside>
</template>

<script setup>
import { ref } from "vue";
import { Home, BarChart, Settings, ChevronLeft, ChevronRight } from "lucide-vue-next";

const collapsed = ref(false);
</script>

<style scoped>
.sidebar {
  width: 220px;
  background-color: #1e293b;
  color: white;
  padding: 20px;
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  opacity: 1;
  transform: translateX(0);
  transition: opacity 0.2s ease, transform 0.2s ease;
  
  white-space: nowrap;
  text-overflow: ellipsis;
}

.sidebar.collapsed .sidebar-title {
  opacity: 0;
  transform: translateX(-10px); /* slight slide left when hidden */
}

.toggle-btn {
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.sidebar ul {
  list-style: none;
  padding: 0;
  margin-top: 20px;
}

.sidebar li {
  margin: 15px 0;
}

.sidebar a {
  display: flex;
  align-items: center;
  gap: 10px;
  color: white;
  text-decoration: none;
  white-space: nowrap;
  line-height: 1;
}

.sidebar a:hover {
  color: #94a3b8; /* slate-400 */
}

.sidebar.collapsed a {
  justify-content: flex-start;
  gap: 10px;
}

.label {
  transition: opacity 0.3s ease, width 0.3s ease;
  overflow: hidden;
  display: inline-block; /* 🔑 prevents baseline shift */
}

.sidebar.collapsed .label {
  opacity: 0;
  width: 0;
  overflow: hidden;
}

.icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;        /* 🔑 icon never shrinks */
  display: flex;         
  align-items: center;   /* 🔑 ensure consistent vertical centering */
}

.chevron {
  width: 20px;
  height: 20px;
}
</style>
