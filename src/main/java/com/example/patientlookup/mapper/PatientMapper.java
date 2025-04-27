package com.example.patientlookup.mapper;

import com.example.patientlookup.dto.PatientResponseDto;
import com.example.patientlookup.model.Patient;
import org.springframework.stereotype.Component;

@Component
public class PatientMapper {
    public PatientResponseDto toResponseDto(Patient patient) {
        if (patient == null) {
            return null;
        }

        PatientResponseDto dto = new PatientResponseDto();
        dto.setId(patient.getId());
        dto.setName(patient.getName());
        dto.setDateOfBirth(patient.getDateOfBirth());
        dto.setEmail(patient.getEmail());
        dto.setAge(patient.getAge());
        dto.setCreatedAt(patient.getCreatedAt());
        dto.setUpdatedAt(patient.getUpdatedAt());
        return dto;
    }
}