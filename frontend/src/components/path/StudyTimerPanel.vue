<template>
  <section class="panel-card panel">
    <div class="head">
      <h3>学习计时器</h3>
      <span class="status" :class="timer.status">{{ statusLabel }}</span>
    </div>
    <p class="desc">开始/暂停/结束后会自动写入学习时长，你仍然可以在提交前手动修改。</p>

    <div class="time">{{ formattedElapsed }}</div>

    <el-form label-position="top">
      <el-form-item label="计时章节">
        <el-select
          :model-value="selectedUnitId"
          placeholder="选择正在学习的章节"
          style="width: 100%"
          @update:model-value="$emit('update:selectedUnitId', $event)"
        >
          <el-option
            v-for="unit in pendingUnits"
            :key="unit.id"
            :label="`#${unit.unit_order} ${unit.unit_title}`"
            :value="unit.id"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <div class="actions">
      <el-button type="primary" :disabled="timer.status === 'running' || timer.status === 'locked'" @click="$emit('start')">
        开始
      </el-button>
      <el-button :disabled="timer.status !== 'running'" @click="$emit('pause')">暂停</el-button>
      <el-button :disabled="timer.status !== 'paused'" @click="$emit('resume')">继续</el-button>
      <el-button :disabled="!['running', 'paused'].includes(timer.status)" @click="$emit('stop')">
        结束并写入
      </el-button>
    </div>

    <p v-if="timer.status === 'locked'" class="hint">当前有另一路线正在计时，请先回到对应路线结束计时。</p>
  </section>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  timer: {
    type: Object,
    default: () => ({ status: "idle", elapsed_seconds: 0 })
  },
  selectedUnitId: {
    type: Number,
    default: null
  },
  pendingUnits: {
    type: Array,
    default: () => []
  }
});

defineEmits(["start", "pause", "resume", "stop", "update:selectedUnitId"]);

const statusLabel = computed(() => {
  if (props.timer.status === "running") return "进行中";
  if (props.timer.status === "paused") return "已暂停";
  if (props.timer.status === "locked") return "已锁定";
  return "未开始";
});

const formattedElapsed = computed(() => {
  const seconds = props.timer.elapsed_seconds || 0;
  const hh = String(Math.floor(seconds / 3600)).padStart(2, "0");
  const mm = String(Math.floor((seconds % 3600) / 60)).padStart(2, "0");
  const ss = String(seconds % 60).padStart(2, "0");
  return `${hh}:${mm}:${ss}`;
});
</script>

<style scoped>
.panel {
  padding: 18px;
  background: linear-gradient(165deg, rgba(15, 118, 110, 0.08), rgba(255, 255, 255, 0.95));
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

h3 {
  margin: 0;
}

.status {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  color: white;
}

.status.running {
  background: #15803d;
}

.status.paused {
  background: #b45309;
}

.status.locked {
  background: #475569;
}

.status.idle {
  background: #64748b;
}

.desc {
  color: var(--muted);
  margin: 8px 0 10px;
}

.time {
  font-family: "Space Grotesk", sans-serif;
  font-size: 44px;
  letter-spacing: 1.2px;
  margin: 2px 0 10px;
  padding: 8px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(25, 52, 65, 0.12);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.actions :deep(.el-button) {
  border-radius: 10px;
}

.actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

.hint {
  margin: 10px 0 0;
  color: #475569;
}
</style>
