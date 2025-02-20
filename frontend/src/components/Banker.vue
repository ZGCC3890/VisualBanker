<template>
  <div class="container">
    <h2>银行家算法模拟</h2>
    <div>
      <label>客户数 (n):</label>
      <input v-model="n" type="number" min="1" />
      <label>资源种类 (m):</label>
      <input v-model="m" type="number" min="1" />
      <button @click="runBanker">运行算法</button>
    </div>

    <div v-if="data">
      <h3>资源信息</h3>
      <p>Available: {{ data.available }}</p>

      <h3>进程信息</h3>
      <table>
        <thead>
          <tr>
            <th>客户</th>
            <th>Max</th>
            <th>Allocation</th>
            <th>Need</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in data.max_resources" :key="index">
            <td>P{{ index }}</td>
            <td>{{ row }}</td>
            <td>{{ data.allocation[index] }}</td>
            <td>{{ data.need[index] }}</td>
          </tr>
        </tbody>
      </table>

      <h3>安全检查</h3>
      <p v-if="data.safe">安全序列: {{ data.sequence }}</p>
      <p v-else style="color: red;">系统处于不安全状态！</p>
    </div>
  </div>
</template>

<script>
import { ref } from "vue";
import { fetchBankerData } from "../api/banker";

export default {
  setup() {
    const n = ref(7);
    const m = ref(4);
    const data = ref(null);

    const runBanker = async () => {
      try {
        data.value = await fetchBankerData(n.value, m.value);
      } catch (error) {
        console.error("请求失败", error);
      }
    };

    return { n, m, data, runBanker };
  },
};
</script>

<style scoped>
.container {
  width: 80%;
  margin: auto;
  text-align: center;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}
table, th, td {
  border: 1px solid black;
}
th, td {
  padding: 8px;
  text-align: center;
}
</style>
