
![Build](https://travis-ci.com/AMOS-5/infinitag.svg?branch=master)

# InfiniTag
The repository for the AMOS Team 5 Project for tagging
documents using the power of machine learning!

## Setup of Database
### MySQL
- Install mysql server
- Create a database with the name `infinitag`
- Make sure you have a user for the database which can read and write
to the database.
- Make sure the following environment variables are set with the values
given when creating a user for the database.
    - `INFINITAG_USER`
    - `INFINITAG_PASSWORD`
- If necessary, set the value for `spring.datasource.url` in the
`application.properties` file.

## Running Software
### Front End
- `cd frontend`
- `npm ci`
- `ng serve`

### Rest Server
- `./mvnw spring-boot:run`
