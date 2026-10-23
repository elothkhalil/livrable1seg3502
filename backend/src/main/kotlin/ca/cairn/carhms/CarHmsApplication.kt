package ca.cairn.carhms

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class CarHmsApplication

fun main(args: Array<String>) {
    runApplication<CarHmsApplication>(*args)
}
