Feature: Get student course list

  Background:
    * url baseUrl

  Scenario: Fetch list of courses

    Given path 'students/Student1/courses'
    And header Content-Type = 'application/json'
    When method GET
    Then status 200
    And match $ == read('courses.json')
