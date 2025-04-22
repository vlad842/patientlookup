package com.example.patientlookup.service;

import com.example.patientlookup.model.Patient;

import java.util.Collection;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import org.springframework.stereotype.Service;

@Service
public class PatientService {
        private final Map<String, Patient> patientDb = new HashMap<>();

        public Collection<Patient> getAllPatients() {
        return patientDb.values();
    }

    public Patient createPatient(Patient patient) {
        String id = UUID.randomUUID().toString();
        patient.setId(id);
        patientDb.put(id, patient);
        return patient;
    }

    public Optional<Patient> getPatientById(String id) {
        return Optional.ofNullable(patientDb.get(id));
    }

    public Optional<Patient> updatePatient(String id, Patient patient) {
        if (patientDb.containsKey(id)) {
            patient.setId(id);
            patientDb.put(id, patient);
            return Optional.of(patient);
        }
        return Optional.empty();
    }

    public boolean deletePatient(String id) {
        return patientDb.remove(id) != null;
    }

    public Optional<Patient> patchPatient(String id, Map<String, Object> updates) {
        return getPatientById(id).map(patient -> {
            updates.forEach((key, value) -> {
                switch (key) {
                    case "name" -> patient.setName((String) value);
                    case "dob" -> patient.setDob((String) value);
                    case "email" -> patient.setEmail((String) value);
                }
            });
            patientDb.put(id, patient);
            return patient;
        });
    }
}
