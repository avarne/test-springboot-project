Feature: Get student course1 details

  Background:
    * url baseUrl

  Scenario: Fetch course1 for student1

    Given path 'students/Student1/courses/Course1'
    And header Content-Type = 'application/json'
    When method GET
    Then status 200
    And match $ == {"id":"#notnull","name":"#notnull","description":"#notnull","steps": "#notnull"}
