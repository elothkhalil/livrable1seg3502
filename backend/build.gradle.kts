plugins {
    kotlin("jvm") version "2.0.21"
    kotlin("plugin.spring") version "2.0.21"
    id("org.springframework.boot") version "3.3.5"
    id("io.spring.dependency-management") version "1.1.6"
}

group = "ca.cairn"
version = "0.1.0"

repositories { mavenCentral() }
kotlin { jvmToolchain(17) }

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin")
    implementation("org.jetbrains.kotlin:kotlin-reflect")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("io.cucumber:cucumber-java:7.20.1")
    testImplementation("io.cucumber:cucumber-junit-platform-engine:7.20.1")
    testImplementation("io.cucumber:cucumber-spring:7.20.1")
    testImplementation("org.junit.platform:junit-platform-suite")
}

tasks.withType<Test> { useJUnitPlatform() }
// Initial feature contracts are specifications, not yet bound to step definitions.
