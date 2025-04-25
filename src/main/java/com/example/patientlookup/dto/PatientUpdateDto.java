package com.example.patientlookup.dto;

import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
public class PatientUpdateDto extends PatientBaseDto {
    // Additional validation specific to updates if needed
} 