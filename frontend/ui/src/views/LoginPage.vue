<template>
  <div>
    <h1>Login</h1>
    <form @submit.prevent="handleLogin">
      <div>
        <label>Username</label>
        <input type="text" v-model="username" required />
      </div>
      <div>
        <label>Password</label>
        <input type="password" v-model="password" required />
      </div>
      <button type="submit">Login</button>
      <p v-if="errorMessage">{{ errorMessage }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const username = ref('');
const password = ref('');
const errorMessage = ref('');
const router = useRouter();

const handleLogin = async () => {
  // Clear any old session data first
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_role');

  try {
    const response = await axios.post('http://127.0.0.1:5000/auth/login', {
      username: username.value,
      password: password.value
    });

    const token = response.data.access_token;
    localStorage.setItem('access_token', token);

    // After getting the token, get the user's profile
    const profileResponse = await axios.get('http://127.0.0.1:5000/auth/profile', {
        headers: { Authorization: `Bearer ${token}` }
    });

    const userRole = profileResponse.data.role;
    localStorage.setItem('user_role', userRole); // Store the user's role

    // Redirect based on role
    if (userRole === 'admin') {
        router.push('/admin/dashboard');
    } else {
        router.push('/dashboard');
    }

  } catch (error) {
    errorMessage.value = 'Invalid credentials. Please try again.';
    console.error('Login failed:', error);
  }
};
</script>