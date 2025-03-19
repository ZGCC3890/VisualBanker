<template>
  <div class="outer-container">
    <h2>云游戏算力分配</h2>
    <div>
      <label>客户数 (n):</label>
      <input v-model.number="n" type="number" min="1" />
    </div>
    <div>
      <label>核心种类 (m):</label>
      <input v-model.number="m" type="number" min="1" />
    </div>
    <div>
      <!-- 输入合法性检查通过再调用runBanker -->
      <button @click="validation">运行算法</button>
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
              {{ item.seq }} (资源利用率: {{ item.utilization.toFixed(2) }}%)
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed , onMounted} from "vue";
import { fetchBankerData } from "../api/banker";

export default {
  setup() {
    const n = ref(5);
    const m = ref(3);
    const data = ref(null);

    const BASE_URL = import.meta.env.BASE_URL;

    const backgroundImages = [
      `${BASE_URL}images/bg1.png`,
      `${BASE_URL}images/bg2.png`,
      `${BASE_URL}images/bg3.png`,
    ];

    onMounted(() => {
      const randomIndex = Math.floor(Math.random() * backgroundImages.length);
      const selectedImage = backgroundImages[randomIndex];
      console.log("Selected background:", selectedImage);

      // **直接修改 body 背景**
      document.body.style.backgroundImage = `url(${selectedImage})`;
    });

    const runBanker = async () => {
      try {
        data.value = await fetchBankerData(n.value, m.value);
      } catch (error) {
        console.error("请求失败：", error);
        alert("网络请求失败，请稍后重试");
      }
    };

    const validation = () => {
      // 检查 n 和 m 是否为大于0的数字
      if (!n.value || n.value <= 0 || !m.value || m.value <= 0) {
        alert("非法输入，请输入大于0的数字");
        return;
      }
      runBanker();
    };

    // 所有安全序列总数
    const totalSequences = computed(() => {
      if (!data.value || !data.value.all_safe_sequences) {
        return 0;
      }
      return data.value.all_safe_sequences.length;
    });

    // 取资源利用率最高的前 10 条安全序列
    const best10Sequences = computed(() => {
      if (!data.value || !data.value.all_safe_sequences || !data.value.utilization_per_sequence) {
        return [];
      }
      // 组合安全序列和资源利用率，并按资源利用率降序排序
      const sequencesWithUtilization = data.value.all_safe_sequences.map((seq, index) => {
        return { seq, utilization: data.value.utilization_per_sequence[index] };
      });

      sequencesWithUtilization.sort((a, b) => b.utilization - a.utilization); // 资源利用率降序排序
      return sequencesWithUtilization.slice(0, 10);
    });

    return {
      n,
      m,
      data,
      validation,
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
