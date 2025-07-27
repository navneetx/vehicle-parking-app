<template>
  <div>
    <h1>Analytics</h1>
    <router-link to="/admin/dashboard">Back to Admin Dashboard</router-link>

    <div v-if="loading">Loading chart data...</div>
    <div v-else class="chart-container">
      <h2>Revenue per Parking Lot</h2>
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';

// Register the necessary components for Chart.js
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const loading = ref(true);
const chartData = ref({
  labels: [],
  datasets: [{
    label: 'Total Revenue (₹)',
    backgroundColor: '#4CAF50',
    data: []
  }]
});

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false
});

onMounted(async () => {
  const token = localStorage.getItem('access_token');
  try {
    const response = await axios.get('http://127.0.0.1:5000/api/admin/revenue', {
      headers: { Authorization: `Bearer ${token}` }
    });

    const revenueSummary = response.data.revenue_summary;

    // Process the API data into the format Chart.js requires
    const labels = revenueSummary.map(item => item.lot_name);
    const data = revenueSummary.map(item => item.total_revenue);

    chartData.value = {
      labels: labels,
      datasets: [{
        label: 'Total Revenue (₹)',
        backgroundColor: '#4CAF50',
        data: data
      }]
    };

  } catch (error) {
    console.error("Failed to fetch analytics data:", error);
  } finally {
    loading.value = false;
  }
});
</script>

<script>
export default {
  name: 'AdminAnalyticsPage'
}
</script>

<style scoped>
  .chart-container {
    position: relative;
    height: 60vh;
    width: 80vw;
    margin-top: 20px;
  }
</style>