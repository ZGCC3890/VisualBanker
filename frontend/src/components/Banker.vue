<template>
  <div class="outer-container">
    <h2>银行家算法模拟</h2>
    <div>
      <label>客户数 (n):</label>
      <input v-model="n" type="number" min="1" />
    </div>
    <div>
      <label>资源种类 (m):</label>
      <input v-model="m" type="number" min="1" />
    </div>
    <div>
      <button @click="runBanker">运行算法</button>
    </div>

    <!-- 只有在 data 不为空时才渲染结果 -->
    <div v-if="data" class="dashboard">
      <!-- 左侧：资源信息 -->
      <div class="section">
        <h3>资源信息</h3>
        <p>Total Resources: {{ data.total_resources }}</p>
        <p>Available: {{ data.available }}</p>
      </div>

      <!-- 中间：进程信息 -->
      <div class="section">
        <h3>进程信息</h3>
        <table>
          <thead>
            <tr>
              <th>客户</th>
              <th>Max</th>
              <th>Allocation</th>
              <th>Need</th>
              <th>Execute Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in data.max_resources" :key="index">
              <td>P{{ index }}</td>
              <td>{{ data.max_resources[index] }}</td>
              <td>{{ data.allocation[index] }}</td>
              <td>{{ data.need[index] }}</td>
              <td>{{ data.execute_time ? data.execute_time[index] : "N/A" }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 右侧：安全检查 -->
      <div class="section">
        <h3>安全检查</h3>
        <p v-if="data.safe">
          系统处于安全状态
        </p>
        <p v-else style="color: red;">
          系统处于不安全状态！
        </p>

        <div v-if="data.safe">
          <p>首个安全序列: {{ data.one_safe_sequence }}</p>
          <p>最佳序列: {{ data.best_sequence }}</p>
          <p>所有安全序列: 共计 {{ totalSequences }} 条</p>

          <ul class="no-point-list">
            <li v-for="(item, idx) in best10Sequences" :key="idx">
              {{ item.seq }} (总执行时间: {{ item.time }})
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from "vue";
import { fetchBankerData } from "../api/banker";

export default {
  setup() {
    const n = ref(5);
    const m = ref(3);
    const data = ref(null);

    const runBanker = async () => {
      try {
        data.value = await fetchBankerData(n.value, m.value);
      } catch (error) {
        console.error("请求失败：", error);
      }
    };

    // 所有安全序列总数
    const totalSequences = computed(() => {
      if (!data.value || !data.value.all_safe_sequences) {
        return 0;
      }
      return data.value.all_safe_sequences.length;
    });

    // 只取“执行时间最短”的前 10 条安全序列
    const best10Sequences = computed(() => {
      if (
        !data.value ||
        !data.value.all_safe_sequences ||
        !data.value.execute_time
      ) {
        return [];
      }
      // 对所有安全序列计算总执行时间并排序
      const sequencesWithTime = data.value.all_safe_sequences.map((seq) => {
        const time = seq.reduce((acc, procIndex) => {
          return acc + data.value.execute_time[procIndex];
        }, 0);
        return { seq, time };
      });
      // 按总执行时间从小到大排序
      sequencesWithTime.sort((a, b) => a.time - b.time);
      // 只取前 10 条
      return sequencesWithTime.slice(0, 10);
    });

    return {
      n,
      m,
      data,
      runBanker,
      totalSequences,
      best10Sequences
    };
  },
};
</script>


<style scoped>
.container {
  width: 80%;
  margin: auto;
  text-align: center;
}
</style>
