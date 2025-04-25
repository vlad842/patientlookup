package com.example.patientlookup.dto;

import lombok.Data;
import java.time.LocalDate;
import java.util.UUID;

@Data
public class PatientResponseDto {
    private UUID id;
    private String name;
    private LocalDate dob;
    private String email;
    private int age;
} 