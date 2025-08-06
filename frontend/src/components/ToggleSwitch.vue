<template>
  <div class="toggle-container">
    <label class="toggle-switch">
      <input
        type="checkbox"
        :checked="modelValue"
        @change="$emit('update:modelValue', $event.target.checked)"
      />
      <span class="slider"></span>
    </label>
    <span class="toggle-label">{{ label }}</span>
  </div>
</template>

<script setup>
defineProps({
  modelValue: Boolean,
  label: {
    type: String,
    default: 'Toggle'
  }
});

defineEmits(['update:modelValue']);
</script>

<style scoped>
.toggle-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin: 1rem 0;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 28px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  background-color: #ccc;
  border-radius: 34px;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  transition: 0.4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  border-radius: 50%;
  transition: 0.4s;
}

input:checked + .slider {
  background-color: #4ade80;
}

input:checked + .slider:before {
  transform: translateX(22px);
}

.toggle-label {
  font-size: 1rem;
  color: #f1f5f9; /* bright text for dark backgrounds */
  font-weight: 500;
}
</style>
