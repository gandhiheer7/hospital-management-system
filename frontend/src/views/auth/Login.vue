<template>
  <div class="row justify-content-center mt-5">
    <div class="col-md-4">
      <div class="card shadow">
        <div class="card-body">
          <h3 class="text-center mb-4">Login</h3>
          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label>Email</label>
              <input v-model="email" type="email" class="form-control" required />
            </div>
            <div class="mb-3">
              <label>Password</label>
              <input v-model="password" type="password" class="form-control" required />
            </div>
            <button type="submit" class="btn btn-primary w-100">Login</button>
          </form>
          <div class="mt-3 text-center">
             <router-link to="/register">Create Patient Account</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../services/api';

const email = ref('');
const password = ref('');
const router = useRouter();

const handleLogin = async () => {
  try {
    const res = await api.post('/auth/login', { email: email.value, password: password.value });
    localStorage.setItem('role', res.data.role);
    localStorage.setItem('user_id', res.data.user_id);
    
    // Redirect based on role
    if (res.data.role === 'admin') router.push('/admin');
    else if (res.data.role === 'doctor') router.push('/doctor');
    else router.push('/patient');
    
    // Force Navbar update
    setTimeout(() => window.location.reload(), 100);
  } catch (err) {
    alert(err.response?.data?.message || 'Login failed');
  }
};
</script>