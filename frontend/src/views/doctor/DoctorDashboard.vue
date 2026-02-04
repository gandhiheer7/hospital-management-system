<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Doctor Dashboard</h2>
      <span v-if="doctorName" class="badge bg-secondary fs-6">Dr. {{ doctorName }}</span>
    </div>

    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      {{ error }}
      <button type="button" class="btn-close" @click="error = ''"></button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-2">Loading appointments...</p>
    </div>

    <div v-else class="card shadow-sm">
      <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Today's Appointments</h5>
        <button class="btn btn-sm btn-light text-primary" @click="fetchDashboard">Refresh</button>
      </div>

      <div class="card-body p-0">
        <div v-if="appointments.length === 0" class="text-center py-5 text-muted">
          <p class="mb-0 fs-5">No upcoming appointments found.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th scope="col">Time</th>
                <th scope="col">Date</th>
                <th scope="col">Patient Name</th>
                <th scope="col">Status</th>
                <th scope="col" class="text-end">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="appt in appointments" :key="appt.id">
                <td><span class="fw-bold">{{ appt.time_slot }}</span></td>
                <td>{{ formatDate(appt.date) }}</td>
                <td>{{ appt.patient_name }}</td>
                <td>
                  <span class="badge bg-warning text-dark">{{ appt.status }}</span>
                </td>
                <td class="text-end">
                  <button 
                    class="btn btn-sm btn-success" 
                    @click="openCompleteModal(appt)"
                    data-bs-toggle="modal" 
                    data-bs-target="#completeVisitModal"
                  >
                    Complete Visit
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="modal fade" id="completeVisitModal" tabindex="-1" aria-hidden="true" ref="modalRef">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-light">
            <h5 class="modal-title">Consultation Details</h5>
            <button 
              type="button" 
              class="btn-close" 
              data-bs-dismiss="modal" 
              aria-label="Close"
              ref="closeModalBtn"
            ></button>
          </div>
          <div class="modal-body">
            
            <div v-if="selectedAppointment" class="alert alert-info d-flex justify-content-between">
              <span><strong>Patient:</strong> {{ selectedAppointment.patient_name }}</span>
              <span><strong>Date:</strong> {{ formatDate(selectedAppointment.date) }}</span>
            </div>

            <form @submit.prevent="submitCompletion">
              <div class="mb-3">
                <label class="form-label fw-bold">Diagnosis <span class="text-danger">*</span></label>
                <textarea 
                  class="form-control" 
                  v-model="form.diagnosis" 
                  rows="2" 
                  placeholder="Enter medical diagnosis..." 
                  required
                ></textarea>
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold">Prescription <span class="text-danger">*</span></label>
                <textarea 
                  class="form-control" 
                  v-model="form.prescription" 
                  rows="3" 
                  placeholder="Enter medication details and dosage..." 
                  required
                ></textarea>
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold">Additional Notes <span class="text-muted">(Optional)</span></label>
                <textarea 
                  class="form-control" 
                  v-model="form.notes" 
                  rows="2" 
                  placeholder="Internal notes or patient instructions..."
                ></textarea>
              </div>

              <div class="modal-footer px-0 pb-0">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="submitting">
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
                  {{ submitting ? 'Submitting...' : 'Mark as Completed' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import apiClient from '../../services/api';

export default {
  name: 'DoctorDashboard',
  data() {
    return {
      doctorName: '',
      appointments: [],
      loading: true,
      submitting: false,
      error: '',
      selectedAppointment: null,
      form: {
        diagnosis: '',
        prescription: '',
        notes: ''
      }
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
        const response = await apiClient.get('/doctor/dashboard');
        this.doctorName = response.data.doctor_name;
        this.appointments = response.data.appointments || [];
      } catch (err) {
        console.error(err);
        this.error = 'Failed to load dashboard data. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    openCompleteModal(appt) {
      this.selectedAppointment = appt;
      // Reset form fields
      this.form = {
        diagnosis: '',
        prescription: '',
        notes: ''
      };
    },
    async submitCompletion() {
      if (!this.selectedAppointment) return;

      this.submitting = true;
      try {
        // Send data to backend
        await apiClient.post(`/doctor/appointment/${this.selectedAppointment.id}/complete`, this.form);
        
        // On success: Remove the appointment from the local list
        this.appointments = this.appointments.filter(a => a.id !== this.selectedAppointment.id);
        
        // Close the modal programmatically by clicking the close button ref
        this.$refs.closeModalBtn.click();
        
      } catch (err) {
        console.error(err);
        alert('Failed to submit consultation details. Please try again.');
      } finally {
        this.submitting = false;
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString();
    }
  }
};
</script>