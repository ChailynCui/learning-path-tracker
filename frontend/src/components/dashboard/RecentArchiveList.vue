<template>
  <section class="panel-card archives">
    <h3>最近归档</h3>
    <div v-if="items.length === 0" class="empty">暂无归档记录</div>
    <ul v-else>
      <li v-for="item in items" :key="item.id">
        <strong>{{ item.path_title }}</strong>
        <span>{{ item.summary_title }}</span>
      </li>
    </ul>
  </section>
</template>

<script setup>
defineProps({
  items: { type: Array, default: () => [] }
});
</script>

<style scoped>
.archives {
  padding: 16px;
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.95), rgba(216, 235, 255, 0.56));
}
h3 {
  margin: 0 0 10px;
  font-size: 22px;
}
ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}
li {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px dashed rgba(25, 52, 65, 0.18);
  padding-bottom: 10px;
  gap: 12px;
}
.empty,
span {
  color: var(--muted);
}
</style>
