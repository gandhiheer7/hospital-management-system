<template>
  <div>
    <h3>Book Appointment</h3>
    
    <div class="row mb-4">
      <div class="col-md-6">
        <label>Filter by Specialization</label>
        <select v-model="selectedDept" @change="fetchDoctors" class="form-select">
          <option value="">All Departments</option>
          <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
      </div>
      <div class="col-md-6">
        <label>Search Doctor</label>
        <input v-model="searchQuery" class="form-control" placeholder="Search by doctor name..." />
      </div>
    </div>

    <div class="row">
      <div class="col-md-6 mb-3" v-for="doc in filteredDoctors" :key="doc.id">
        <div class="card h-100 shadow-sm">
          <div class="card-body">
            <h5 class="card-title text-primary">{{ doc.name }}</h5>
            <h6 class="card-subtitle mb-2 text-muted">{{ doc.specialization }}</h6>
            <hr>
            <h6>Availability:</h6>
            <div v-if="Object.keys(doc.availability).length">
               <div v-for="(times, day) in doc.availability" :key="day" class="mb-1">
                 <strong>{{ day }} ({{ getNextDate(day) }}):</strong> 
                 <span v-for="t in times" :key="t" 
                       class="badge bg-light text-dark border ms-1 cursor-pointer hover-bg-primary"
                       @click="selectSlot(doc.id, day, t)">
                   {{ t }}
                 </span>
               </div>
            </div>
            <div v-else class="text-muted small">No schedule available.</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedSlot" class="alert alert-info mt-3 position-fixed bottom-0 end-0 m-3 shadow" style="z-index: 1000; min-width: 300px;">
      <h5>Confirm Booking</h5>
      <p><strong>Doctor:</strong> {{ getDoctorName(selectedSlot.doctorId) }}</p>
      <p><strong>Time:</strong> {{ selectedSlot.time }}</p>
      
      <label>Date (YYYY-MM-DD):</label>
      <input v-model="bookingDate" type="date" class="form-control mb-2" readonly />
      
      <div class="d-flex gap-2">
        <button @click="confirmBooking" class="btn btn-success flex-grow-1">Confirm</button>
        <button @click="selectedSlot = null" class="btn btn-secondary flex-grow-1">Cancel</button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../../services/api';

const departments = ref([]);
const doctors = ref([]);
const selectedDept = ref('');
const searchQuery = ref('');
const selectedSlot = ref(null);
const bookingDate = ref('');

onMounted(async () => {
  try {
    const deptRes = await api.get('/patient/departments');
    departments.value = deptRes.data;
    fetchDoctors();
  } catch (e) {
    console.error("Error loading data", e);
  }
});

const fetchDoctors = async () => {
  const url = selectedDept.value ? `/patient/doctors?specialization_id=${selectedDept.value}` : '/patient/doctors';
  const res = await api.get(url);
  doctors.value = res.data;
};

// Client-side Search Logic
const filteredDoctors = computed(() => {
  if (!searchQuery.value) return doctors.value;
  return doctors.value.filter(d => d.name.toLowerCase().includes(searchQuery.value.toLowerCase()));
});

// Helper to get next upcoming date for a given day name
const getNextDate = (dayName) => {
  const dayMap = { "Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6 };
  if (!(dayName in dayMap)) return ""; 

  const targetDayIdx = dayMap[dayName];
  const date = new Date();
  const currentDayIdx = date.getDay();
  
  let daysToAdd = targetDayIdx - currentDayIdx;
  if (daysToAdd <= 0) daysToAdd += 7; // Always next occurrence (1-7 days away)

  date.setDate(date.getDate() + daysToAdd);
  return date.toISOString().split('T')[0];
};

const getDoctorName = (id) => {
  const doc = doctors.value.find(d => d.id === id);
  return doc ? doc.name : 'Unknown';
};

const selectSlot = (doctorId, day, time) => {
  // Auto-fill the date based on the day clicked
  const dateStr = getNextDate(day);
  bookingDate.value = dateStr;
  selectedSlot.value = { doctorId, day, time };
};

const confirmBooking = async () => {
  if (!bookingDate.value) return alert('Error: Date missing');
  try {
    await api.post('/patient/book', {
      doctor_id: selectedSlot.value.doctorId,
      date: bookingDate.value,
      time_slot: selectedSlot.value.time
    });
    alert('Booking Confirmed!');
    selectedSlot.value = null;
  } catch (err) {
    alert(err.response?.data?.message || 'Failed');
  }
};
</script>

<style scoped>
.cursor-pointer { cursor: pointer; }
.hover-bg-primary:hover { background-color: #0d6efd !important; color: white !important; }
</style>