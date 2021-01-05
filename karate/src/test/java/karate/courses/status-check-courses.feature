Feature: check status of data returned by the courses API
  Background:
    * url baseUrl
    * header Accept = 'application/json'
  Scenario: List courses
    Given   path 'students/Student1/courses'
    When method get
    Then status 200
