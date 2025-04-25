# Build stage
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

# Run stage
FROM openjdk:17-jdk-slim
WORKDIR /app
COPY --from=build /app/target/patientlookup-0.0.1-SNAPSHOT.jar ./app.jar
COPY src/main/resources/application-prod.properties ./application-prod.properties

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar", "--spring.config.location=classpath:/application.properties,file:./application-prod.properties"]
