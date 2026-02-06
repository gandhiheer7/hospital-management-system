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

    <h4 class="mt-4">All Appointments</h4>
    <div class="table-responsive">
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Patient</th>
                    <th>Doctor</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="apt in appointments" :key="apt.id">
                    <td>{{ apt.date }} {{ apt.time_slot }}</td>
                    <td>{{ apt.patient_name }}</td>
                    <td>{{ apt.doctor_name }}</td>
                    <td>{{ apt.status }}</td>
                    <td>
                        <button v-if="apt.status === 'Booked'" @click="cancelAppointment(apt.id)" class="btn btn-sm btn-danger">Cancel</button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';

const stats = ref(null);
const appointments = ref([]);

const fetchData = async () => {
  try {
    const res = await api.get('/admin/dashboard');
    stats.value = res.data.stats;
    const aptRes = await api.get('/admin/appointments');
    appointments.value = aptRes.data;
  } catch (err) {
    console.error(err);
  }
};

const cancelAppointment = async (id) => {
    if(!confirm('Force cancel this appointment?')) return;
    try {
        await api.put(`/admin/appointments/${id}/cancel`);
        fetchData(); // Refresh list
    } catch (err) {
        alert('Error cancelling');
    }
};

onMounted(fetchData);
</script>