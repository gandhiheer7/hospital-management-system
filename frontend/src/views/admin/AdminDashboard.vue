<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Admin Dashboard</h2>
      <button class="btn btn-outline-primary" @click="fetchData">Refresh Data</button>
    </div>

    <div v-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else>
      <div class="row mb-4">
        <div class="col-md-4">
          <div class="card text-white bg-primary mb-3">
            <div class="card-header">Registered Doctors</div>
            <div class="card-body">
              <h1 class="card-title">{{ stats.doctors }}</h1>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card text-white bg-success mb-3">
            <div class="card-header">Registered Patients</div>
            <div class="card-body">
              <h1 class="card-title">{{ stats.patients }}</h1>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card text-white bg-info mb-3">
            <div class="card-header">Total Appointments</div>
            <div class="card-body">
              <h1 class="card-title">{{ stats.appointments }}</h1>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">All System Appointments</div>
        <div class="card-body">
          <div v-if="appointments.length === 0" class="text-center text-muted py-3">
            No appointments found.
          </div>
          <div v-else class="table-responsive">
            <table class="table table-striped table-hover">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Patient Name</th>
                  <th>Doctor Name</th>
                  <th>Date</th>
                  <th>Time Slot</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="appt in appointments" :key="appt.id">
                  <td>{{ appt.id }}</td>
                  <td>{{ appt.patient_name }}</td>
                  <td>{{ appt.doctor_name }}</td>
                  <td>{{ formatDate(appt.date) }}</td>
                  <td>{{ appt.time_slot }}</td>
                  <td>
                    <span 
                      class="badge" 
                      :class="{
                        'bg-warning text-dark': appt.status === 'Booked',
                        'bg-success': appt.status === 'Completed',
                        'bg-danger': appt.status === 'Cancelled'
                      }"
                    >
                      {{ appt.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import apiClient from '../../services/api';

export default {
  name: 'AdminDashboard',
  data() {
    return {
      stats: {
        doctors: 0,
        patients: 0,
        appointments: 0
      },
      appointments: [],
      loading: true,
      error: ''
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.error = '';
      
      try {
        // Fetch Stats
        const statsRes = await apiClient.get('/admin/dashboard');
        this.stats = statsRes.data.stats;

        // Fetch Appointments
        const apptRes = await apiClient.get('/admin/appointments');
        this.appointments = apptRes.data || { doctors: 0, patients: 0, appointments: 0 };

      } catch (err) {
        console.error(err);
        this.error = 'Failed to load dashboard data. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleDateString();
    }
  }
};
</script>