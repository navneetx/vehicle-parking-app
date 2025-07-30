<template>
  <div class="admin-dashboard">
    <h1>Admin Dashboard</h1>
    <p>Welcome, Admin! Select a task below to manage the parking system.</p>
    
    <nav class="dashboard-nav">
      <router-link to="/admin/lots" class="nav-card">
        <h2>Manage Parking Lots</h2>
        <p>Create, view, edit, and delete parking lots and their spots.</p>
      </router-link>
      
      <router-link to="/admin/users" class="nav-card">
        <h2>View All Users</h2>
        <p>See a complete list of all registered users in the system.</p>
      </router-link>
      
      <router-link to="/admin/analytics" class="nav-card">
        <h2>View Analytics</h2>
        <p>Check the revenue summary and other key metrics.</p>
      </router-link>
    </nav>
  </div>
</template>

<script>

export default {
  name: 'AdminDashboardPage'
}
</script>

<style scoped>
.admin-dashboard {
  max-width: 900px;
  margin: 20px auto;
  text-align: center;
}

.dashboard-nav {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.nav-card {
  display: block;
  width: 250px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 10px;
  text-decoration: none;
  color: #333;
  background-color: #f9f9f9;
  transition: transform 0.2s, box-shadow 0.2s;
}

.nav-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.nav-card h2 {
  margin-top: 0;
  color: #0056b3;
}

.nav-card p {
  font-size: 0.9em;
  color: #666;
}
</style>