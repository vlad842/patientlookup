package com.example.patientlookup.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import lombok.Data;
import org.springframework.data.domain.Sort;

@Data
public class PatientSearchRequest {
    private String name;

    @Min(0)
    private int page = 0;

    @Min(1)
    @Max(50)
    private int size = 10;

    private String sortBy = "name";
    private String direction = "asc";

    public Sort.Direction getSortDirection() {
        return Sort.Direction.fromString(direction.toLowerCase());
    }
}