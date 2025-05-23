package com.example.patientlookup.model;

import lombok.Data;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.Period;
import java.util.UUID;

import com.example.patientlookup.dto.PatientCreateDto;
import com.example.patientlookup.dto.PatientUpdateDto;
import com.fasterxml.jackson.annotation.JsonProperty;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Past;

@Entity
@Data
@Table(name = "patient")
public class Patient {
    public Patient(PatientCreateDto patientDto) {
        this.name = patientDto.getName();
        this.dateOfBirth = patientDto.getDateOfBirth();
        this.email = patientDto.getEmail();
    }

    public Patient() {}
    
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @NotBlank(message = "Name is required")
    private String name;

    @NotNull(message = "Date of birth is required")
    @Past(message = "Date of birth must be in the past")
    @Column(name = "date_of_birth")
    @JsonProperty("dateOfBirth")
    private LocalDate dateOfBirth;

    @Email(message = "Invalid email address")
    private String email;

    @Column(name = "created_at")
    @JsonProperty(access = JsonProperty.Access.READ_ONLY)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    @JsonProperty(access = JsonProperty.Access.READ_ONLY)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    public int getAge() {
        return Period.between(dateOfBirth, LocalDate.now()).getYears();
    }

    public void updateFromDto(PatientUpdateDto patientDto) {
        if (patientDto.getName() != null) {
            this.name = patientDto.getName();
        }
        if (patientDto.getDateOfBirth() != null) {
            this.dateOfBirth = patientDto.getDateOfBirth();
        }
        if (patientDto.getEmail() != null) {
            this.email = patientDto.getEmail();
        }
    }
}
