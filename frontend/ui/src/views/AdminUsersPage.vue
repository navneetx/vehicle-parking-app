<template>
  <div class="users-container">
    <div class="header">
      <h1>View All Users</h1>
      <router-link to="/admin/dashboard" class="back-link">← Back to Admin Dashboard</router-link>
    </div>

    <div class="content-card">
      <!-- Search Form -->
      <div class="search-form">
        <form @submit.prevent="fetchUsers">
          <input type="text" v-model="searchQuery" placeholder="Search by username..." />
          <button type="submit">Search</button>
        </form>
      </div>

      <div v-if="loading">Loading users...</div>
      <table v-else class="users-table">
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
            <td class="role-cell" :class="user.role">{{ user.role }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

// --- State Management ---
const users = ref([]);
const loading = ref(true);
const searchQuery = ref(''); // Holds the admin's search input.

// --- API Function ---
// Fetches the list of users from the backend.
// It can also send a search query to filter the results.
const fetchUsers = async () => {
  const token = localStorage.getItem('access_token');
  try {
    loading.value = true;
    // Append the search query to the URL as a parameter if it exists.
    const url = `http://127.0.0.1:5000/api/admin/users?username=${searchQuery.value}`;
    
    const response = await axios.get(url, {
      headers: { Authorization: `Bearer ${token}` }
    });
    users.value = response.data.users;
  } catch (error) {
    console.error("Failed to fetch users:", error);
  } finally {
    loading.value = false;
  }
};

// --- Lifecycle Hook ---
// `onMounted` runs when the component is first loaded, triggering the initial data fetch.
onMounted(fetchUsers);
</script>

<style scoped>
.users-container {
  max-width: 900px;
  margin: 20px auto;
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 30px;
}
.back-link {
  text-decoration: none;
  color: #007bff;
  font-weight: bold;
}
.content-card {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.search-form {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}
.search-form input {
  flex-grow: 1;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.search-form button {
  padding: 8px 15px;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}
.users-table {
  width: 100%;
  border-collapse: collapse;
}
.users-table th, .users-table td {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: left;
}
.users-table th {
  background-color: #f8f9fa;
}
.role-cell {
  text-transform: capitalize;
  font-weight: bold;
}
.role-cell.admin {
  color: #dc3545; /* Red */
}
.role-cell.user {
  color: #28a745; /* Green */
}
</style>