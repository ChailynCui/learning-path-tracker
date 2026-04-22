<template>
  <section class="stats-grid">
    <article class="panel-card stat" v-for="item in cards" :key="item.label">
      <p class="label">{{ item.label }}</p>
      <p class="value">{{ item.value }}</p>
    </article>
  </section>
</template>

<script setup>
defineProps({
  cards: { type: Array, default: () => [] }
});
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(130px, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}
.stat {
  padding: 14px 16px;
  background:
    linear-gradient(150deg, rgba(255, 255, 255, 0.95), rgba(227, 246, 241, 0.65));
}
.label {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}
.value {
  margin: 6px 0 0;
  font-size: 30px;
  font-family: "Space Grotesk", sans-serif;
  line-height: 1.05;
}
@media (max-width: 860px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(120px, 1fr));
  }
}
</style>
