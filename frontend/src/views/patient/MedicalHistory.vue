<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Medical History</h2>
      <button 
        class="btn btn-outline-success" 
        @click="exportHistory" 
        :disabled="exporting || history.length === 0"
      >
        <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>
        {{ exporting ? 'Exporting...' : 'Export to CSV' }}
      </button>
    </div>

    <div v-if="exportMessage" class="alert alert-success alert-dismissible fade show" role="alert">
      {{ exportMessage }}
      <button type="button" class="btn-close" @click="exportMessage = ''"></button>
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
      <div v-if="history.length === 0" class="text-center text-muted py-5 bg-light rounded">
        <h4>No medical history found.</h4>
        <p>Completed appointments with diagnoses will appear here.</p>
      </div>

      <div v-else class="card">
        <div class="card-body table-responsive p-0">
          <table class="table table-hover table-striped mb-0">
            <thead class="table-dark">
              <tr>
                <th scope="col">Date</th>
                <th scope="col">Doctor</th>
                <th scope="col" style="width: 25%">Diagnosis</th>
                <th scope="col" style="width: 25%">Prescription</th>
                <th scope="col">Notes</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in history" :key="record.id">
                <td class="text-nowrap">{{ formatDate(record.date) }}</td>
                <td>Dr. {{ record.doctor_name }}</td>
                <td>{{ record.diagnosis }}</td>
                <td>
                  <pre class="mb-0" style="font-family: inherit; white-space: pre-wrap;">{{ record.prescription }}</pre>
                </td>
                <td class="text-muted small">
                  {{ record.notes || 'N/A' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import apiClient from '../../services/api';

export default {
  name: 'MedicalHistory',
  data() {
    return {
      history: [],
      loading: true,
      exporting: false,
      error: '',
      exportMessage: ''
    };
  },
  mounted() {
    this.fetchHistory();
  },
  methods: {
    async fetchHistory() {
      this.loading = true;
      this.error = '';
      try {
        const response = await apiClient.get('/patient/history');
        this.history = response.data;
      } catch (err) {
        console.error(err);
        this.error = 'Failed to load medical history.';
      } finally {
        this.loading = false;
      }
    },
    async exportHistory() {
      this.exporting = true;
      this.exportMessage = '';
      try {
        // Triggers the Celery Async Job
        await apiClient.post('/patient/export');
        this.exportMessage = 'Export started! You will receive an email shortly.';
      } catch (err) {
        console.error(err);
        this.error = 'Failed to start export job.';
      } finally {
        this.exporting = false;
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }
  }
};
</script>