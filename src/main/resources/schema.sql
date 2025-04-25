-- Drop existing table if it exists
DROP TABLE IF EXISTS patient;

-- Create the patient table with the correct schema
CREATE TABLE patient (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
); 