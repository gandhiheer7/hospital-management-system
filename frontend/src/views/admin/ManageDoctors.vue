<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Manage Doctors</h2>
      <button 
        class="btn btn-primary" 
        @click="openModal('create')"
      >
        <i class="bi bi-person-plus"></i> Add New Doctor
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
        <div v-if="doctors.length === 0" class="text-center text-muted py-4">
          No doctors found.
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Specialization</th>
                <th>Status</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doc in doctors" :key="doc.id">
                <td>{{ doc.id }}</td>
                <td>{{ doc.name }}</td>
                <td>{{ doc.email }}</td>
                <td>{{ doc.specialization }}</td>
                <td>
                  <span 
                    class="badge" 
                    :class="doc.is_approved ? 'bg-success' : 'bg-secondary'"
                  >
                    {{ doc.is_approved ? 'Active' : 'Blocked' }}
                  </span>
                </td>
                <td class="text-end">
                  <button 
                    class="btn btn-sm btn-outline-primary me-2"
                    @click="openModal('edit', doc)"
                  >
                    Edit
                  </button>
                  
                  <button 
                    v-if="doc.is_approved"
                    class="btn btn-sm btn-outline-warning me-2"
                    @click="toggleStatus(doc.id, false)"
                  >
                    Block
                  </button>
                  <button 
                    v-else
                    class="btn btn-sm btn-outline-success me-2"
                    @click="toggleStatus(doc.id, true)"
                  >
                    Approve
                  </button>

                  <button 
                    class="btn btn-sm btn-outline-danger"
                    @click="deleteDoctor(doc.id)"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="modal fade" id="doctorModal" tabindex="-1" aria-hidden="true" ref="modalRef">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Edit Doctor' : 'Add New Doctor' }}</h5>
            <button 
              type="button" 
              class="btn-close" 
              data-bs-dismiss="modal" 
              aria-label="Close"
              ref="closeModalBtn"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitForm">
              
              <div class="mb-3">
                <label class="form-label">Full Name <span class="text-danger">*</span></label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="form.name" 
                  required
                >
              </div>

              <div class="mb-3">
                <label class="form-label">Email Address <span class="text-danger">*</span></label>
                <input 
                  type="email" 
                  class="form-control" 
                  v-model="form.email" 
                  :disabled="isEditing" 
                  required
                >
                <div v-if="isEditing" class="form-text">Email cannot be changed.</div>
              </div>

              <div class="mb-3" v-if="!isEditing">
                <label class="form-label">Password <span class="text-danger">*</span></label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="form.password" 
                  required
                >
              </div>

              <div class="mb-3">
                <label class="form-label">Specialization ID <span class="text-danger">*</span></label>
                <input 
                  type="number" 
                  class="form-control" 
                  v-model.number="form.specialization_id" 
                  required
                  min="1"
                >
                <div class="form-text">Enter the numeric ID of the department.</div>
              </div>

              <div class="mb-3" v-if="isEditing">
                <label class="form-label">Availability (JSON)</label>
                <textarea 
                  class="form-control" 
                  v-model="form.availability" 
                  rows="3"
                  placeholder='e.g. {"Monday": ["09:00", "10:00"]}'
                ></textarea>
                <div class="form-text">Edit day-wise time slots in JSON format.</div>
              </div>

              <div class="d-grid">
                <button type="submit" class="btn btn-primary">
                  {{ isEditing ? 'Save Changes' : 'Create Doctor' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <button id="modalTrigger" class="d-none" data-bs-toggle="modal" data-bs-target="#doctorModal"></button>

  </div>
</template>

<script>
import apiClient from '../../services/api';

export default {
  name: 'ManageDoctors',
  data() {
    return {
      doctors: [],
      loading: true,
      error: '',
      isEditing: false,
      editId: null,
      form: {
        name: '',
        email: '',
        password: '',
        specialization_id: '',
        availability: ''
      }
    };
  },
  mounted() {
    this.fetchDoctors();
  },
  methods: {
    async fetchDoctors() {
      this.loading = true;
      this.error = '';
      try {
        const response = await apiClient.get('/admin/doctors');
        this.doctors = response.data;
      } catch (err) {
        console.error(err);
        this.error = 'Failed to fetch doctors list.';
      } finally {
        this.loading = false;
      }
    },
    
    openModal(mode, doctor = null) {
      this.isEditing = mode === 'edit';
      this.error = ''; // Clear errors

      if (mode === 'edit' && doctor) {
        this.editId = doctor.id;
        // Populate form
        this.form = {
          name: doctor.name,
          email: doctor.email,
          specialization_id: doctor.specialization_id || '', // Note: API might need to return this ID
          availability: JSON.stringify(doctor.availability || {}, null, 2),
          password: '' // Not used in edit
        };
      } else {
        // Reset form for create
        this.editId = null;
        this.form = {
          name: '',
          email: '',
          password: '',
          specialization_id: '',
          availability: ''
        };
      }

      // Trigger Modal
      document.getElementById('modalTrigger').click();
    },

    async submitForm() {
      try {
        if (this.isEditing) {
          // Edit Logic
          // Note: Availability parsing is handled here
          const payload = {
            name: this.form.name,
            specialization_id: this.form.specialization_id,
            availability: this.form.availability // Backend should handle JSON parsing if implemented
          };
          
          await apiClient.put(`/admin/doctors/${this.editId}`, payload);
          alert('Doctor updated successfully');
        } else {
          // Create Logic
          await apiClient.post('/admin/doctors', {
            name: this.form.name,
            email: this.form.email,
            password: this.form.password,
            specialization_id: this.form.specialization_id
          });
          alert('Doctor created successfully');
        }

        // Close Modal & Refresh
        this.$refs.closeModalBtn.click();
        this.fetchDoctors();

      } catch (err) {
        console.error(err);
        const msg = err.response?.data?.message || 'Operation failed.';
        alert(`Error: ${msg}`);
      }
    },

    async toggleStatus(id, newStatus) {
      if (!confirm(`Are you sure you want to ${newStatus ? 'approve' : 'block'} this doctor?`)) return;

      try {
        await apiClient.put(`/admin/doctors/${id}/status`, {
          is_approved: newStatus
        });
        
        // Optimistic UI Update
        const doc = this.doctors.find(d => d.id === id);
        if (doc) doc.is_approved = newStatus;

      } catch (err) {
        console.error(err);
        alert('Failed to update status.');
      }
    },

    async deleteDoctor(id) {
      if (!confirm('Are you sure you want to permanently delete this doctor? This action cannot be undone.')) return;

      try {
        await apiClient.delete(`/admin/doctors/${id}`);
        // Remove from list
        this.doctors = this.doctors.filter(d => d.id !== id);
      } catch (err) {
        console.error(err);
        alert('Failed to delete doctor. Ensure no appointments are linked.');
      }
    }
  }
};
</script>