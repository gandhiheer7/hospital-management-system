<template>
  <div class="container mt-4">
    <h2>Book an Appointment</h2>
    <p class="text-muted">
      Select a doctor, choose a date, and pick an available time slot.
    </p>

    <!-- Success -->
    <div
      v-if="successMessage"
      class="alert alert-success alert-dismissible fade show"
      role="alert"
    >
      {{ successMessage }}
      <button type="button" class="btn-close" @click="successMessage = ''"></button>
    </div>

    <!-- Error -->
    <div v-if="errorMessage" class="alert alert-danger" role="alert">
      {{ errorMessage }}
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Form -->
    <div v-else class="card">
      <div class="card-body">
        <form @submit.prevent="submitBooking">

          <!-- Doctor -->
          <div class="mb-3">
            <label class="form-label">
              Select Doctor <span class="text-danger">*</span>
            </label>
            <select
              class="form-select"
              v-model="form.doctor_id"
              @change="onDoctorChange"
              required
            >
              <option value="" disabled>-- Choose a Doctor --</option>
              <option
                v-for="doc in doctors"
                :key="doc.id"
                :value="doc.id"
              >
                Dr. {{ doc.name }} ({{ doc.specialization }})
              </option>
            </select>
          </div>

          <!-- Date -->
          <div class="mb-3">
            <label class="form-label">
              Appointment Date <span class="text-danger">*</span>
            </label>
            <input
              type="date"
              class="form-control"
              v-model="form.date"
              :min="minDate"
              :max="maxDate"
              @change="updateAvailableSlots"
              required
            >
            <div class="form-text">
              Appointments can be booked up to 7 days in advance.
            </div>
          </div>

          <!-- Slots -->
          <div class="mb-4">
            <label class="form-label">
              Available Time Slots <span class="text-danger">*</span>
            </label>

            <div v-if="!form.doctor_id || !form.date" class="text-muted fst-italic">
              Please select a doctor and date to view available slots.
            </div>

            <div
              v-else-if="availableSlots.length === 0"
              class="alert alert-warning py-2"
            >
              No slots available for {{ formattedDate }}.
            </div>

            <div v-else class="d-flex flex-wrap gap-2">
              <template v-for="slot in availableSlots" :key="slot">
                <input
                  type="radio"
                  class="btn-check"
                  name="timeSlot"
                  :id="'slot-' + slot"
                  :value="slot"
                  v-model="form.time_slot"
                >
                <label
                  class="btn btn-outline-primary"
                  :for="'slot-' + slot"
                >
                  {{ slot }}
                </label>
              </template>
            </div>
          </div>

          <!-- Submit -->
          <div class="d-grid">
            <button
              type="submit"
              class="btn btn-success"
              :disabled="submitting || !isFormValid"
            >
              <span
                v-if="submitting"
                class="spinner-border spinner-border-sm me-2"
              ></span>
              {{ submitting ? 'Booking...' : 'Confirm Appointment' }}
            </button>
          </div>

        </form>
      </div>
    </div>
  </div>
</template>

<script>
import apiClient from '../../services/api';

export default {
  name: 'BookAppointment',

  data() {
    const today = new Date();
    const max = new Date();
    max.setDate(today.getDate() + 7);

    return {
      doctors: [],
      loading: true,
      submitting: false,
      errorMessage: '',
      successMessage: '',
      availableSlots: [],
      minDate: today.toISOString().split('T')[0],
      maxDate: max.toISOString().split('T')[0],
      form: {
        doctor_id: '',
        date: '',
        time_slot: ''
      }
    };
  },

  computed: {
    isFormValid() {
      return (
        this.form.doctor_id &&
        this.form.date &&
        this.form.time_slot
      );
    },
    formattedDate() {
      if (!this.form.date) return '';
      return new Date(this.form.date).toLocaleDateString(undefined, {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }
  },

  mounted() {
    this.fetchDoctors();
  },

  methods: {
    async fetchDoctors() {
      this.loading = true;
      this.errorMessage = '';

      try {
        const { data } = await apiClient.get('/patient/doctors');
        this.doctors = Array.isArray(data) ? data : [];
      } catch (err) {
        console.error(err);
        this.errorMessage = 'Failed to load doctors list.';
      } finally {
        this.loading = false;
      }
    },

    onDoctorChange() {
      this.availableSlots = [];
      this.form.time_slot = '';
      if (this.form.date) {
        this.updateAvailableSlots();
      }
    },

    updateAvailableSlots() {
      this.availableSlots = [];
      this.form.time_slot = '';

      if (!this.form.doctor_id || !this.form.date) return;

      const doctor = this.doctors.find(
        d => String(d.id) === String(this.form.doctor_id)
      );
      if (!doctor || !doctor.availability) return;

      const dayName = new Date(this.form.date).toLocaleDateString('en-US', {
        weekday: 'long'
      });

      if (Array.isArray(doctor.availability[dayName])) {
        this.availableSlots = doctor.availability[dayName];
      }
    },

    async submitBooking() {
      if (!this.isFormValid) return;

      this.submitting = true;
      this.errorMessage = '';
      this.successMessage = '';

      try {
        await apiClient.post('/patient/book', { ...this.form });

        this.successMessage = 'Appointment booked successfully!';
        this.form = { doctor_id: '', date: '', time_slot: '' };
        this.availableSlots = [];

        setTimeout(() => {
          this.$router.push('/patient/dashboard');
        }, 1500);

      } catch (err) {
        console.error(err);
        this.errorMessage =
          err?.response?.data?.message ||
          'Failed to book appointment. Please try again.';
      } finally {
        this.submitting = false;
      }
    }
  }
};
</script>
