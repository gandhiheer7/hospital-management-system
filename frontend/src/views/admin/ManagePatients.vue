<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Manage Patients</h2>
      <button class="btn btn-outline-primary" @click="fetchPatients">
        <i class="bi bi-arrow-clockwise"></i> Refresh List
      </button>
    </div>

    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      {{ error }}
      <button type="button" class="btn-close" @click="error = ''"></button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else class="card shadow-sm">
      <div class="card-body p-0">
        <div v-if="patients.length === 0" class="text-center text-muted py-5">
          <p class="mb-0 fs-5">No patients found in the system.</p>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th class="text-center">Total Appointments</th>
                <th>Status</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="patient in patients" :key="patient.id">
                <td>{{ patient.id }}</td>
                <td>
                  <span class="fw-bold">{{ patient.name }}</span>
                  <div class="small text-muted" v-if="patient.contact_info">
                    {{ patient.contact_info }}
                  </div>
                </td>
                <td>{{ patient.email }}</td>
                <td class="text-center">
                  <span class="badge bg-info text-dark">
                    {{ patient.appointment_count || 0 }}
                  </span>
                </td>
                <td>
                  <span 
                    class="badge" 
                    :class="patient.is_blocked ? 'bg-danger' : 'bg-success'"
                  >
                    {{ patient.is_blocked ? 'Blocked' : 'Active' }}
                  </span>
                </td>
                <td class="text-end">
                  <button 
                    v-if="patient.is_blocked"
                    class="btn btn-sm btn-outline-success"
                    @click="toggleStatus(patient.id, false)"
                    title="Reactivate Patient"
                  >
                    Unblock
                  </button>
                  <button 
                    v-else
                    class="btn btn-sm btn-outline-danger"
                    @click="toggleStatus(patient.id, true)"
                    title="Deactivate Patient"
                  >
                    Block
                  </button>
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
  name: 'ManagePatients',
  data() {
    return {
      patients: [],
      loading: true,
      error: ''
    };
  },
  mounted() {
    this.fetchPatients();
  },
  methods: {
    async fetchPatients() {
      this.loading = true;
      this.error = '';
      try {
        // Fetching all patients as per requirements
        const response = await apiClient.get('/admin/patients');
        this.patients = response.data;
      } catch (err) {
        console.error(err);
        this.error = 'Failed to load patient list.';
      } finally {
        this.loading = false;
      }
    },
    async toggleStatus(id, shouldBlock) {
      const action = shouldBlock ? 'block' : 'unblock';
      if (!confirm(`Are you sure you want to ${action} this patient?`)) return;

      try {
        await apiClient.put(`/admin/patients/${id}/block`, {
          is_blocked: shouldBlock
        });

        // Optimistic UI update
        const patient = this.patients.find(p => p.id === id);
        if (patient) {
          patient.is_blocked = shouldBlock;
        }
      } catch (err) {
        console.error(err);
        this.error = `Failed to ${action} patient.`;
      }
    }
  }
};
</script>