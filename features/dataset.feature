Feature: The dataset resources

  Background:
    Given saber is running
    Given the following users exist
    | display_name   | email        | password  |
    | dave           | dave@foo.com | secret    |

  Scenario: All endpoints are discoverable from root
    When I get the 'root' resource
    Then I should see a link to the 'user' resource
