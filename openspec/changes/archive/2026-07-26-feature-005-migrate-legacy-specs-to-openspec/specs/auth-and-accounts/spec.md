## ADDED Requirements

### Requirement: Login Password Authentication

The system MUST provide login/password authentication for protected upload and download flows.

#### Scenario: Valid login grants upload access

- **GIVEN** a user has valid login/password credentials
- **WHEN** the user signs in successfully
- **THEN** the system issues an authenticated session or token
- **AND** protected upload flows can use that authentication state

#### Scenario: Invalid login denies upload access

- **GIVEN** submitted credentials are invalid
- **WHEN** the user attempts to sign in
- **THEN** the system denies authentication
- **AND** no file content is accepted as an authenticated upload

### Requirement: Configurable Account Provisioning

The system MUST support deployment-configured account provisioning where self-service registration may be enabled or disabled.

#### Scenario: Registration disabled

- **GIVEN** self-service registration is disabled by deployment configuration
- **WHEN** an unauthenticated user attempts to create an account
- **THEN** the system denies self-service registration
- **AND** the response explains that account creation is unavailable without exposing internal rules

### Requirement: OAuth Deferred Availability

The system MUST treat Google OAuth as optional deferred behavior unless explicitly enabled by a future feature.

#### Scenario: OAuth not shipped

- **GIVEN** Google OAuth has not been enabled for the deployment
- **WHEN** a user reviews available sign-in methods
- **THEN** login/password remains the supported authentication path
- **AND** OAuth absence does not block browser upload, CLI upload, or download work
