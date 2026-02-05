<template>
  <div class="row justify-content-center mt-5">
    <div class="col-md-6">
      <div class="card shadow">
        <div class="card-body">
          <h3 class="text-center">Register Patient</h3>
          <form @submit.prevent="register">
            <div class="mb-2"><label>Name</label><input v-model="form.name" class="form-control" required></div>
            <div class="mb-2"><label>Email</label><input v-model="form.email" type="email" class="form-control" required></div>
            <div class="mb-2"><label>Password</label><input v-model="form.password" type="password" class="form-control" required></div>
            <div class="mb-2"><label>Date of Birth</label><input v-model="form.dob" type="date" class="form-control"></div>
            <div class="mb-2"><label>Contact</label><input v-model="form.contact_info" class="form-control"></div>
            <div class="mb-3"><label>Address</label><textarea v-model="form.address" class="form-control"></textarea></div>
            <button class="btn btn-success w-100">Register</button>
          </form>
          <div class="mt-3 text-center">
             <router-link to="/login">Already have an account? Login</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../services/api';

const router = useRouter();
const form = reactive({ name: '', email: '', password: '', dob: '', contact_info: '', address: '' });

const register = async () => {
  try {
    await api.post('/auth/register', form);
    alert('Registration successful! Please login.');
    router.push('/login');
  } catch (err) {
    alert(err.response?.data?.message || 'Error');
  }
};
</script>