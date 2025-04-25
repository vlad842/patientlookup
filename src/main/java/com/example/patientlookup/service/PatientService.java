package com.example.patientlookup.service;

import com.example.patientlookup.model.Patient;
import com.example.patientlookup.repository.PatientRepository;
import com.example.patientlookup.dto.PatientResponseDto;
import com.example.patientlookup.dto.PaginatedResponse;
import com.example.patientlookup.mapper.PatientMapper;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.time.LocalDate;
import java.util.stream.Collectors;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

@Service
public class PatientService {
    private final PatientRepository patientRepository;
    private final PatientMapper patientMapper;

    public PatientService(PatientRepository patientRepository, PatientMapper patientMapper) {
        this.patientRepository = patientRepository;
        this.patientMapper = patientMapper;
    }

    public List<Patient> getAllPatients() {
        return patientRepository.findAll();
    }

    public Patient createPatient(Patient patient) {
       return patientRepository.save(patient);
    }

    public Optional<Patient> getPatientById(UUID id) {
        return patientRepository.findById(id);
    }
   
    public PaginatedResponse<PatientResponseDto> getPatients(String name, Pageable pageable) {
        Page<Patient> page;
        if (name != null && !name.isBlank()) {
            page = patientRepository.findByNameContainingIgnoreCase(name, pageable);
        } else {
            page = patientRepository.findAll(pageable);
        }

        List<PatientResponseDto> content = page.getContent().stream()
            .map(patientMapper::toResponseDto)
            .collect(Collectors.toList());

        return new PaginatedResponse<>(
            content,
            page.getTotalElements(),
            page.getNumber()
        );
    }
   
    public Optional<Patient> updatePatient(UUID id, Patient updatedPatient) {
        return getPatientById(id).map(existingPatient -> {
            existingPatient.setName(updatedPatient.getName());
            existingPatient.setDob(updatedPatient.getDob());
            existingPatient.setEmail(updatedPatient.getEmail());
            return patientRepository.save(existingPatient);
        });
    }

    public boolean deletePatient(UUID id) {
        if (patientRepository.existsById(id)) {
            patientRepository.deleteById(id);
            return true;
        }
        return false;
    }

    public Optional<Patient> patchPatient(UUID id, Map<String, Object> updates) {
        return getPatientById(id).map(patient -> {
            updates.forEach((key, value) -> {
                switch (key) {
                    case "name" -> patient.setName((String) value);
                    case "dob" -> patient.setDob((LocalDate) value);
                    case "email" -> patient.setEmail((String) value);
                }
            });
            return patientRepository.save(patient);
        });
    }
}
