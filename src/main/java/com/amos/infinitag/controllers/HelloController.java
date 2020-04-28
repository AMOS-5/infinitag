package com.amos.infinitag.controllers;

import com.amos.infinitag.models.Health;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;

@CrossOrigin(origins = "http://localhost:4200")
@RestController
public class HelloController {


    @RequestMapping("/")
    public String index() {
        return "Greetings from Spring Boot!";
    }

    @RequestMapping("/health")
    public Health getHealth() {
        return new Health();
    }

}
