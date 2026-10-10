<script setup>
defineProps({ point: Object, width: Number, height: Number, month: String, value: String })
</script>

<template>
  <div
    v-if="point" class="chart-tooltip" role="tooltip"
    :style="{
      '--tip-x': `${point.x / width * 100}%`,
      '--tip-y': `${point.y / height * 100}%`,
      '--tip-offset': point.y < 80 ? '12px' : 'calc(-100% - 12px)',
    }"
  >
    <span>{{ month }}</span>
    <strong>{{ value }}</strong>
  </div>
</template>
