package karate.courses;
//package com.rkdevblog.karate.employee;

import com.intuit.karate.junit5.Karate;

public class ITStudentIntegrationTest {

    @Karate.Test
    Karate testCoursesApiHealth() {
        return Karate.run("status-check-courses").relativeTo(getClass());
    }

    @Karate.Test
    Karate testGetStudentCourses() {
        return Karate.run("get-courses").relativeTo(getClass());
    }

    @Karate.Test
    Karate testGetCourse1() {
        return Karate.run("getstudent-course1").relativeTo(getClass());
    }

   /*@Karate.Test
    Karate testAddEmployee() {
        return Karate.run("create-employee").relativeTo(getClass());
    }

    @Karate.Test
    Karate testGetEmployee() {
        return Karate.run("get-employee").relativeTo(getClass());
    }*/

}
