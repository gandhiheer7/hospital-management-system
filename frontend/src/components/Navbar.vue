<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary" v-if="role">
    <div class="container-fluid">
      <a class="navbar-brand" href="#">HMS</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item" v-if="role === 'admin'">
            <router-link class="nav-link" to="/admin">Dashboard</router-link>
          </li>
          <li class="nav-item" v-if="role === 'admin'">
            <router-link class="nav-link" to="/admin/doctors">Doctors</router-link>
          </li>
          <li class="nav-item" v-if="role === 'admin'">
            <router-link class="nav-link" to="/admin/patients">Patients</router-link>
          </li>

          <li class="nav-item" v-if="role === 'doctor'">
            <router-link class="nav-link" to="/doctor">Dashboard</router-link>
          </li>

          <li class="nav-item" v-if="role === 'patient'">
            <router-link class="nav-link" to="/patient">Dashboard</router-link>
          </li>
          <li class="nav-item" v-if="role === 'patient'">
            <router-link class="nav-link" to="/patient/book">Book Appointment</router-link>
          </li>
          <li class="nav-item" v-if="role === 'patient'">
            <router-link class="nav-link" to="/patient/history">History</router-link>
          </li>
           <li class="nav-item" v-if="role === 'patient'">
            <router-link class="nav-link" to="/patient/profile">Profile</router-link>
          </li>
        </ul>
        <div class="d-flex">
          <button class="btn btn-danger btn-sm" @click="logout">Logout</button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const router = useRouter();
const role = ref(localStorage.getItem('role'));

const logout = async () => {
  try {
    await api.post('/auth/logout');
  } catch (err) {
    console.error(err);
  } finally {
    localStorage.clear();
    role.value = null;
    router.push('/login');
  }
};
</script>