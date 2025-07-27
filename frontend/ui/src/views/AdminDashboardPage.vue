<template>
  <div>
    <h1>Admin Dashboard</h1>
    <p>Welcome, Admin! Here you can manage the parking system.</p>
    <nav>
      <router-link to="/admin/lots">Manage Parking Lots</router-link>
      <router-link to="/admin/users">View All Users</router-link>
      <router-link to="/admin/analytics">View Analytics</router-link>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboardPage'
}
</script>

<style scoped>
  nav {
    margin-top: 20px;
    font-size: 1.2em;
  }
  nav a {
    margin: 0 15px; /* Adds space between the links */
    text-decoration: none;
    color: #2c3e50;
    font-weight: bold;
  }
  nav a:first-child {
    margin-left: 0; /* Removes extra space from the first link */
  }
  nav a:hover {
    text-decoration: underline;
  }
</style>