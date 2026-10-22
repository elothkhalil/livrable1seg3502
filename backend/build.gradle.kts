plugins {
    kotlin("jvm") version "2.0.21"
}
repositories { mavenCentral() }
kotlin { jvmToolchain(17) }
// Initial feature contracts are specifications, not yet bound to step definitions.
// No Cucumber execution task is claimed by this deliverable.
