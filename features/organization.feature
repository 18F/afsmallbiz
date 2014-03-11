Feature: The organization resources

  Background:
    Given podserve is running
    Given the following users exist
    | display_name   | email  | password |
    | dave | dave@fogmine.com | secret |

  Scenario: The organization resource returns all organizations
    Given the following organizations exist
    | title   | description  |
    | something | a really cool organization with vague name |
    | another | another really cool organization |
    When I get the 'organization' resource
    Then I should see 2 links for the '/rel/organization' relation
