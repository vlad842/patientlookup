package com.example.patientlookup.dto;

import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
public class PatientCreateDto extends PatientBaseDto {
    // Additional validation specific to creation if needed
}