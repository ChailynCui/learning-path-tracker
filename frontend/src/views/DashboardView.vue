<template>
  <MotivationBanner
    :title="dashboard.title"
    :streak="dashboard.current_streak"
    :motivation="dashboard.motivation"
  />

  <StatsCards :cards="statCards" />
  <TodayTaskCard :task="dashboard.today_task" @continue="goPath" @complete="quickComplete" />

  <section class="dashboard-grid">
    <div class="left-column">
      <section class="panel-card section">
        <div class="section-head">
          <h3>今天复习什么</h3>
          <span class="count-pill">{{ dashboard.today_reviews.length }} 项</span>
        </div>
        <div v-if="dashboard.today_reviews.length === 0" class="empty-block">
          <p class="empty-title">今天暂无复习队列</p>
          <p class="empty-sub">保持节奏，先推进一章新内容。</p>
        </div>
        <ul v-else class="review-list">
          <li v-for="item in dashboard.today_reviews" :key="`${item.path_id}-${item.unit_id}`">
            <div>
              <strong>{{ item.unit_title }}</strong>
              <p>{{ item.path_title }}</p>
            </div>
            <div class="actions">
              <el-button size="small" @click="goPath(item.path_id)">去详情</el-button>
              <el-button size="small" type="primary" plain @click="quickReview(item)">完成复习</el-button>
            </div>
          </li>
        </ul>
      </section>

      <section class="panel-card section">
        <div class="section-head">
          <h3>周目标</h3>
          <span class="count-pill goal">{{ dashboard.weekly_goal.completed }}/{{ dashboard.weekly_goal.target }}</span>
        </div>
        <div class="goal-row">
          <el-input-number v-model="weeklyGoalTarget" :min="1" :max="99" />
          <el-button type="primary" @click="saveWeeklyGoal">保存目标</el-button>
        </div>
        <el-progress :percentage="dashboard.weekly_goal.progress" :stroke-width="12" />
        <p class="hint">延期章节：{{ dashboard.weekly_goal.overdue_units }} 章</p>
        <ul v-if="dashboard.weekly_goal.overdue_titles.length" class="overdue-list">
          <li v-for="title in dashboard.weekly_goal.overdue_titles" :key="title">{{ title }}</li>
        </ul>
      </section>

      <section class="panel-card section">
        <div class="section-head">
          <h3>备份恢复</h3>
          <span class="count-pill">JSON</span>
        </div>
        <p class="hint">导出当前学习数据，或导入历史备份快速恢复。</p>
        <div class="backup-actions">
          <el-button @click="downloadBackup">导出备份</el-button>
          <el-button type="primary" plain @click="openImportPicker">导入备份</el-button>
          <span class="file-name">{{ selectedBackupName || "未选择文件" }}</span>
        </div>
        <input
          ref="importFileInput"
          class="hidden-input"
          type="file"
          accept=".json,application/json"
          @change="uploadBackup"
        />
      </section>
    </div>

    <div class="right-column">
      <section class="panel-card section">
        <div class="section-head">
          <h3>进行中路线</h3>
          <span class="count-pill">{{ dashboard.routes.length }}</span>
        </div>
        <section class="route-grid">
          <LearningPathCard
            v-for="route in dashboard.routes"
            :key="route.id"
            :route="route"
            @detail="goPath"
          />
          <div v-if="dashboard.routes.length === 0" class="empty-block">
            <p class="empty-title">你还没有进行中的路线</p>
            <p class="empty-sub">去创建路线页导入一个新计划吧。</p>
          </div>
        </section>
      </section>

      <RecentArchiveList :items="archives" />
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";

import {
  completeUnit,
  exportBackup,
  fetchArchives,
  fetchDashboard,
  importBackup,
  reviewUnit,
  updateWeeklyGoal
} from "../api/learning";
import LearningPathCard from "../components/dashboard/LearningPathCard.vue";
import MotivationBanner from "../components/dashboard/MotivationBanner.vue";
import RecentArchiveList from "../components/dashboard/RecentArchiveList.vue";
import StatsCards from "../components/dashboard/StatsCards.vue";
import TodayTaskCard from "../components/dashboard/TodayTaskCard.vue";

const router = useRouter();
const importFileInput = ref(null);
const selectedBackupName = ref("");
const weeklyGoalTarget = ref(5);
const dashboard = ref({
  title: "今天继续推进你的学习主线",
  ongoing_paths: 0,
  completed_units: 0,
  total_xp: 0,
  completed_paths: 0,
  current_level: 1,
  current_streak: 0,
  motivation: "",
  today_task: {},
  routes: [],
  today_reviews: [],
  weekly_goal: {
    target: 5,
    completed: 0,
    progress: 0,
    overdue_units: 0,
    overdue_titles: []
  }
});
const archives = ref([]);

const statCards = computed(() => [
  { label: "正在学习路线数", value: dashboard.value.ongoing_paths },
  { label: "已完成章节数", value: dashboard.value.completed_units },
  {
    label: "本周目标进度",
    value: `${dashboard.value.weekly_goal.completed}/${dashboard.value.weekly_goal.target}`
  },
  { label: "已完成路线数", value: dashboard.value.completed_paths }
]);

const loadData = async () => {
  try {
    const [dashRes, archiveRes] = await Promise.all([fetchDashboard(), fetchArchives()]);
    dashboard.value = dashRes.data;
    weeklyGoalTarget.value = dashRes.data.weekly_goal.target;
    archives.value = archiveRes.data.slice(0, 3);
  } catch (error) {
    ElMessage.error("加载 Dashboard 失败，请先启动后端服务。");
  }
};

const goPath = (id) => {
  if (!id) return;
  router.push(`/paths/${id}`);
};

const quickComplete = async (task) => {
  if (!task.path_id || !task.unit_id) return;
  try {
    const { value } = await ElMessageBox.prompt("请输入本章学习时长（分钟）", "记录学习时长", {
      confirmButtonText: "确认",
      cancelButtonText: "取消",
      inputValue: "30",
      inputPattern: /^[1-9]\d{0,2}$/,
      inputErrorMessage: "请输入 1-999 的整数分钟"
    });

    await completeUnit(task.path_id, task.unit_id, {
      study_minutes: Number(value),
      comment: "今日任务已完成"
    });
    ElMessage.success("本章已完成，今日学习状态已更新。");
    await loadData();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("标记完成失败。");
    }
  }
};

const quickReview = async (item) => {
  try {
    const { value } = await ElMessageBox.prompt(
      `请输入「${item.unit_title}」复习时长（分钟）`,
      "记录复习",
      {
        confirmButtonText: "确认",
        cancelButtonText: "取消",
        inputValue: "15",
        inputPattern: /^[1-9]\d{0,2}$/,
        inputErrorMessage: "请输入 1-999 的整数分钟"
      }
    );
    await reviewUnit(item.path_id, item.unit_id, {
      study_minutes: Number(value),
      comment: `复习完成：${item.unit_title}`
    });
    ElMessage.success("已完成复习，队列已更新。");
    await loadData();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("复习记录失败。");
    }
  }
};

const saveWeeklyGoal = async () => {
  try {
    await updateWeeklyGoal(weeklyGoalTarget.value);
    ElMessage.success("本周目标已更新。");
    await loadData();
  } catch (error) {
    ElMessage.error("周目标更新失败。");
  }
};

const downloadBackup = async () => {
  try {
    const res = await exportBackup();
    const blob = new Blob([JSON.stringify(res.data, null, 2)], {
      type: "application/json;charset=utf-8"
    });
    const link = document.createElement("a");
    const now = new Date();
    const filename = `learning-backup-${now.toISOString().slice(0, 10)}.json`;
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
    ElMessage.success("备份文件已导出。");
  } catch (error) {
    ElMessage.error("导出失败。");
  }
};

const openImportPicker = () => {
  importFileInput.value?.click();
};

const uploadBackup = async (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  selectedBackupName.value = file.name;
  try {
    const content = await file.text();
    const parsed = JSON.parse(content);
    const data = parsed.data || parsed;
    await importBackup(data);
    ElMessage.success("备份已导入。");
    await loadData();
  } catch (error) {
    ElMessage.error("导入失败，请检查 JSON 文件格式。");
  } finally {
    event.target.value = "";
  }
};

onMounted(loadData);
</script>

<style scoped>
.dashboard-grid {
  display: grid;
  grid-template-columns: 1.25fr 1fr;
  gap: 14px;
}

.left-column,
.right-column {
  display: grid;
  gap: 14px;
  align-content: start;
}

.section {
  padding: 16px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.section-head h3 {
  margin: 0;
  font-size: 21px;
}

.count-pill {
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  color: #33576a;
  border: 1px solid rgba(16, 42, 58, 0.18);
  background: rgba(255, 255, 255, 0.85);
}

.count-pill.goal {
  color: #176454;
  border-color: rgba(15, 118, 110, 0.22);
  background: rgba(217, 239, 234, 0.82);
}

.empty-block {
  border: 1px dashed rgba(16, 42, 58, 0.24);
  border-radius: 14px;
  padding: 14px;
}

.empty-title {
  margin: 0;
  font-weight: 700;
}

.empty-sub {
  margin: 6px 0 0;
  color: var(--muted);
}

.review-list,
.overdue-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}

.review-list li {
  border: 1px solid rgba(16, 42, 58, 0.12);
  border-radius: 12px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.74);
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}

.review-list p {
  margin: 5px 0 0;
  color: var(--muted);
}

.actions {
  display: flex;
  gap: 6px;
}

.goal-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.hint {
  margin: 12px 0 8px;
  color: var(--muted);
}

.overdue-list li {
  border-radius: 10px;
  padding: 8px 10px;
  background: rgba(255, 239, 219, 0.6);
  color: #805634;
}

.backup-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-name {
  color: var(--muted);
  font-size: 13px;
}

.hidden-input {
  display: none;
}

.route-grid {
  display: grid;
  gap: 12px;
}

@media (max-width: 980px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .goal-row,
  .backup-actions,
  .actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
