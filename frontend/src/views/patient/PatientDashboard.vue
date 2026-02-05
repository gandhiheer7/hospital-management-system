<template>
  <div v-if="data">
    <h2>Welcome, {{ data.patient_name }}</h2>

    <div class="row mt-4">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header bg-info text-white">Find Care</div>
          <div class="card-body">
            <p>Browse specialists and book your visit.</p>
            <router-link to="/patient/book" class="btn btn-primary">Book Appointment</router-link>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card">
          <div class="card-header bg-warning">Actions</div>
          <div class="card-body">
            <router-link to="/patient/history" class="btn btn-outline-dark me-2">View History</router-link>
            <router-link to="/patient/profile" class="btn btn-outline-secondary">Edit Profile</router-link>
          </div>
        </div>
      </div>
    </div>

    <h4 class="mt-4">Upcoming Appointments</h4>
    <div v-if="data.upcoming_appointments.length === 0" class="alert alert-light">No upcoming visits.</div>
    <ul class="list-group">
      <li v-for="apt in data.upcoming_appointments" :key="apt.id" class="list-group-item d-flex justify-content-between align-items-center">
        <div>
          <strong>Dr. {{ apt.doctor_name }}</strong> <br>
          <small>{{ apt.date }} at {{ apt.time_slot }}</small>
        </div>
        <span class="badge bg-primary">{{ apt.status }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';

const data = ref(null);

onMounted(async () => {
  const res = await api.get('/patient/dashboard');
  data.value = res.data;
});
</script>