CREATE TABLE IF NOT EXISTS reference.dim_identity_grain (
    identity_grain_code VARCHAR PRIMARY KEY,
    description VARCHAR NOT NULL,
    requires_facility_id BOOLEAN NOT NULL,
    active_flag BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS reference.dim_readiness_status (
    readiness_status_code VARCHAR PRIMARY KEY,
    description VARCHAR NOT NULL,
    analytical_activation_allowed BOOLEAN NOT NULL,
    active_flag BOOLEAN NOT NULL
);
