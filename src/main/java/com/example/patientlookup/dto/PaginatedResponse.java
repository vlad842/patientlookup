package com.example.patientlookup.dto;

import lombok.Data;
import java.util.List;

@Data
public class PaginatedResponse<T> {
    private List<T> result;
    private long count;
    private int page;

    public PaginatedResponse(List<T> result, long count, int page) {
        this.result = result;
        this.count = count;
        this.page = page;
    }
}