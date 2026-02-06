<template>
  <div v-if="data">
    <h2>Welcome, {{ data.patient_name }}</h2>

    <div class="row mt-4">
      <div class="col-md-6">
        <div class="card shadow-sm h-100">
          <div class="card-header bg-info text-white">Find Care</div>
          <div class="card-body">
            <p>Browse specialists and book your visit.</p>
            <router-link to="/patient/book" class="btn btn-primary">Book Appointment</router-link>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card shadow-sm h-100">
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
        <div class="d-flex gap-2">
           <span class="badge bg-primary">{{ apt.status }}</span>
           <button v-if="apt.status === 'Booked'" @click="cancelAppointment(apt.id)" class="btn btn-sm btn-danger">Cancel</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';

const data = ref(null);

const fetchData = async () => {
  const res = await api.get('/patient/dashboard');
  data.value = res.data;
};

const cancelAppointment = async (id) => {
    if(!confirm('Are you sure you want to cancel this appointment?')) return;
    try {
        await api.put(`/patient/appointments/${id}/cancel`);
        alert('Appointment Cancelled');
        fetchData();
    } catch (err) {
        alert(err.response?.data?.message || 'Error');
    }
};

onMounted(fetchData);
</script>