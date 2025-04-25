package com.example.patientlookup.controller;
import com.example.patientlookup.model.Patient;
import com.example.patientlookup.dto.*;
import com.example.patientlookup.mapper.PatientMapper;
import org.springframework.web.bind.annotation.*;
import com.example.patientlookup.service.PatientService;

import jakarta.validation.Valid;

import java.util.*;
import java.util.UUID;

import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/patients")
public class PatientController {
    private static final int MAX_PAGE_SIZE = 50;

    private final PatientService patientService;
    private final PatientMapper patientMapper;

    public PatientController(PatientService patientService, PatientMapper patientMapper) {
        this.patientService = patientService;
        this.patientMapper = patientMapper;
    }

    @GetMapping
    public PaginatedResponse<PatientResponseDto> getPatients(@Valid PatientSearchRequest searchRequest) {
        PageRequest pageRequest = PageRequest.of(
            searchRequest.getPage(), 
            Math.min(searchRequest.getSize(), MAX_PAGE_SIZE), 
            Sort.by(searchRequest.getSortDirection(), searchRequest.getSortBy())
        );
        
        return patientService.getPatients(searchRequest.getName(), pageRequest);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public PatientResponseDto createPatient(@Valid @RequestBody PatientCreateDto patientDto) {
        Patient patient = new Patient();
        patient.setName(patientDto.getName());
        patient.setDob(patientDto.getDob());
        patient.setEmail(patientDto.getEmail());
        return patientMapper.toResponseDto(patientService.createPatient(patient));
    }

    @GetMapping("/{id}")
    public PatientResponseDto getPatientById(@PathVariable UUID id) {
        return patientService.getPatientById(id)
                .map(patientMapper::toResponseDto)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Patient not found"));
    }

    @PutMapping("/{id}")
    public PatientResponseDto updatePatient(@PathVariable UUID id, @Valid @RequestBody PatientUpdateDto patientDto) {
        Patient patient = new Patient();
        patient.setName(patientDto.getName());
        patient.setDob(patientDto.getDob());
        patient.setEmail(patientDto.getEmail());
        return patientService.updatePatient(id, patient)
                .map(patientMapper::toResponseDto)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Patient not found"));
    }

    @PatchMapping("/{id}")
    public PatientResponseDto patchPatient(@PathVariable UUID id, @RequestBody Map<String, Object> updates) {
        return patientService.patchPatient(id, updates)
                .map(patientMapper::toResponseDto)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Patient not found"));
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deletePatient(@PathVariable UUID id) {
        if (!patientService.deletePatient(id)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Patient not found");
        }
    }
}