<template>
  <div>
    <h2>Admin Dashboard</h2>
    <div class="row mt-4" v-if="stats">
      <div class="col-md-4">
        <div class="card text-white bg-primary mb-3">
          <div class="card-body">
            <h5 class="card-title">Doctors</h5>
            <p class="card-text display-4">{{ stats.doctors }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-white bg-success mb-3">
          <div class="card-body">
            <h5 class="card-title">Patients</h5>
            <p class="card-text display-4">{{ stats.patients }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-white bg-warning mb-3">
          <div class="card-body">
            <h5 class="card-title">Appointments</h5>
            <p class="card-text display-4">{{ stats.appointments }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';

const stats = ref(null);

onMounted(async () => {
  try {
    const res = await api.get('/admin/dashboard');
    stats.value = res.data.stats;
  } catch (err) {
    console.error(err);
  }
});
</script>