Sample Planguage Requirements
**********************************

..
    This is using the default "interpreted text role" for Planguage's <<vague>> markup.  I should find out if there's a
        a way to change the default role to a new one, and to add meaning/processing to that role.  See
        http://docutils.sf.net/docs/ref/rst/roles.html.

Automation
^^^^^^^^^^^^

..  freq:: Park.Fauna.Squirrels

    :gist: The park will contain squirrels.
    :description: A number of :term:`squirrels` must live in the :term:`park`.
    :source: Bob
    :When: 1.2
    :Sub-functions:
    :Implemented By:
    :Quality Requirements: :pr:`Park.Fauna.Squirrels.Noticeable`
    :Test:
    :Rationale:
    :Value:
    :Assumptions:
    :Dependencies:
    :Risks:
    :Issues:
    :Priority Level: High
    :Status: Pending


..  preq:: Park.Fauna.Squirrels.Noticeable

    :gist: The squirrels must be `reasonably` noticeable.
    :desc: The squirrels must catch the attention of park users, human and otherwise, directly or indirectly.
    :meter: Number of dogs distracted per hour, during `peak times`.
    :level Goal: 3
    :level Wish: 10
    :rationale: If the squirrels aren't noticeable, nobody will derive pleasure from seeing them, in which case
        we may as well not have them.
