<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Patient Dashboard</h2>
      <span v-if="patientName" class="text-muted fw-bold">Welcome, {{ patientName }}</span>
    </div>

    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      {{ error }}
      <button type="button" class="btn-close" @click="error = ''"></button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-2">Loading dashboard...</p>
    </div>

    <div v-else>
      <div class="mb-4 d-flex gap-2">
        <router-link to="/patient/book" class="btn btn-primary">
          <i class="bi bi-calendar-plus"></i> Book Appointment
        </router-link>
        <router-link to="/patient/history" class="btn btn-outline-secondary">
          <i class="bi bi-clock-history"></i> Medical History
        </router-link>
      </div>

      <div class="card shadow-sm">
        <div class="card-header bg-white">
          <h5 class="mb-0 text-primary">Upcoming Appointments</h5>
        </div>
        
        <div class="card-body p-0">
          <div v-if="upcoming.length === 0" class="text-center text-muted py-5">
            <p class="mb-2 lead">No upcoming appointments scheduled.</p>
            <router-link to="/patient/book" class="btn btn-sm btn-outline-primary">Book Now</router-link>
          </div>

          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th scope="col">Date</th>
                  <th scope="col">Time</th>
                  <th scope="col">Doctor</th>
                  <th scope="col">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="appt in upcoming" :key="appt.id">
                  <td>{{ formatDate(appt.date) }}</td>
                  <td><span class="fw-bold text-dark">{{ appt.time_slot }}</span></td>
                  <td>Dr. {{ appt.doctor_name }}</td>
                  <td>
                    <span class="badge bg-warning text-dark border border-warning">
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
  name: 'PatientDashboard',
  data() {
    return {
      patientName: '',
      upcoming: [],
      loading: true,
      error: ''
    };
  },
  mounted() {
    this.fetchDashboard();
  },
  methods: {
    async fetchDashboard() {
      this.loading = true;
      this.error = '';
      try {
        const response = await apiClient.get('/patient/dashboard');
        // Assuming backend returns: { patient_name: 'Name', upcoming_appointments: [] }
        this.patientName = response.data.patient_name;
        this.upcoming = response.data.upcoming_appointments || [];
      } catch (err) {
        console.error("Dashboard fetch error:", err);
        this.error = 'Failed to load dashboard data. Please refresh the page.';
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      return new Date(dateStr).toLocaleDateString(undefined, options);
    }
  }
};
</script>