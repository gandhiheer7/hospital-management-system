<template>
  <div>
    <h3>Doctor Dashboard</h3>
    
    <div class="card mb-4">
      <div class="card-body">
         <h5>Update Availability</h5>
         <p class="small text-muted">Format: JSON {"Monday": ["09:00", "10:00"]}</p>
         <textarea v-model="scheduleJson" class="form-control" rows="3"></textarea>
         <button @click="updateSchedule" class="btn btn-secondary mt-2">Update Schedule</button>
      </div>
    </div>

    <h4>Assigned Appointments</h4>
    <div v-for="apt in appointments" :key="apt.id" class="card mb-2 border-primary">
      <div class="card-body d-flex justify-content-between">
        <div>
          <h5>{{ apt.patient_name }}</h5>
          <p>{{ apt.date }} at {{ apt.time_slot }}</p>
        </div>
        <div>
          <button @click="openCompleteModal(apt)" class="btn btn-success">Complete Visit</button>
        </div>
      </div>
    </div>
    
    <div v-if="selectedApt" class="modal d-block" style="background: rgba(0,0,0,0.5)">
       <div class="modal-dialog">
         <div class="modal-content">
           <div class="modal-header"><h5>Complete Appointment</h5></div>
           <div class="modal-body">
             <input v-model="treatment.diagnosis" placeholder="Diagnosis" class="form-control mb-2">
             <input v-model="treatment.prescription" placeholder="Prescription" class="form-control mb-2">
             <textarea v-model="treatment.notes" placeholder="Notes" class="form-control mb-2"></textarea>
           </div>
           <div class="modal-footer">
             <button @click="selectedApt=null" class="btn btn-secondary">Close</button>
             <button @click="submitTreatment" class="btn btn-primary">Save</button>
           </div>
         </div>
       </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '../../services/api';

const appointments = ref([]);
const scheduleJson = ref('{}');
const selectedApt = ref(null);
const treatment = reactive({ diagnosis: '', prescription: '', notes: '' });

const fetchDashboard = async () => {
  const res = await api.get('/doctor/dashboard');
  appointments.value = res.data.appointments;
};

const updateSchedule = async () => {
  try {
    const json = JSON.parse(scheduleJson.value); // Validate JSON
    await api.put('/doctor/availability', { schedule: json });
    alert('Availability updated');
  } catch (e) {
    alert('Invalid JSON format');
  }
};

const openCompleteModal = (apt) => {
  selectedApt.value = apt;
};

const submitTreatment = async () => {
  try {
    await api.post(`/doctor/appointment/${selectedApt.value.id}/complete`, treatment);
    alert('Visit Completed');
    selectedApt.value = null;
    fetchDashboard();
  } catch (e) {
    alert('Error');
  }
};

onMounted(fetchDashboard);
</script>