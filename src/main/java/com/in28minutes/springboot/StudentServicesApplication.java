package com.in28minutes.springboot;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.support.SpringBootServletInitializer;
import org.springframework.boot.builder.SpringApplicationBuilder;

@SpringBootApplication
public class StudentServicesApplication extends SpringBootServletInitializer {

	public static void main(String[] args) {
		SpringApplication.run(StudentServicesApplication.class, args);
	}

	@Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder application) {
                return application.sources(StudentServicesApplication.class);
    }
}
