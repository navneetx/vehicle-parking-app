<template>
  <div>
    <h1>View All Users</h1>
    <router-link to="/admin/dashboard">Back to Admin Dashboard</router-link>

    <div v-if="loading">Loading users...</div>
    <table v-else>
      <thead>
        <tr>
          <th>User ID</th>
          <th>Username</th>
          <th>Role</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.role }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const users = ref([]);
const loading = ref(true);

const fetchUsers = async () => {
  const token = localStorage.getItem('access_token');
  try {
    const response = await axios.get('http://127.0.0.1:5000/api/admin/users', {
      headers: { Authorization: `Bearer ${token}` }
    });
    users.value = response.data.users;
  } catch (error) {
    console.error("Failed to fetch users:", error);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchUsers);
</script>

<script>
export default {
  name: 'AdminUsersPage'
}
</script>

<style scoped>
  table { width: 100%; border-collapse: collapse; margin-top: 20px; }
  th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
  th { background-color: #f2f2f2; }
</style>