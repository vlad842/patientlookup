package com.example.patientlookup.model;
import lombok.Data;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

@Data
public class Patient {
    @NotBlank(message = "Name is required")
    private String name;
    @NotBlank(message = "Date of birth is required")
    private String dob;
    private String id;
    @Email(message = "Invalid email address")
    private String email;
}
