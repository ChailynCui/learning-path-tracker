<template>
  <section class="panel-card banner">
    <div class="left">
      <p class="task">{{ title }}</p>
      <p class="motivation">{{ motivation }}</p>
    </div>
    <div class="chips">
      <span>连续 {{ streak }} 天</span>
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: { type: String, default: "今天继续推进你的学习主线" },
  streak: { type: Number, default: 0 },
  motivation: { type: String, default: "" }
});
</script>

<style scoped>
.banner {
  padding: 22px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  background:
    radial-gradient(circle at 0% 10%, rgba(15, 118, 110, 0.18), transparent 38%),
    linear-gradient(145deg, rgba(255, 255, 255, 0.94), rgba(222, 245, 240, 0.65));
}
.task {
  font-size: 30px;
  font-family: "Space Grotesk", sans-serif;
  margin: 0;
  letter-spacing: -0.3px;
}
.motivation {
  margin: 8px 0 0;
  color: var(--muted);
  max-width: 650px;
}

.chips {
  display: grid;
  gap: 8px;
}

.chips span {
  display: inline-flex;
  justify-content: center;
  border-radius: 999px;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 700;
  border: 1px solid rgba(15, 118, 110, 0.2);
  background: rgba(255, 255, 255, 0.86);
}

@media (max-width: 760px) {
  .banner {
    flex-direction: column;
    align-items: flex-start;
  }
  .task {
    font-size: 24px;
  }
}
</style>
