## Access Pattern

We receive Immunisation Events in json format via our API. Each message contains inlined resources i.e. it doesn't
contain a reference/link to a preexisting resource. For example, a vaccination event contains the full patient resource
embedded in it. This means our backend doesn't assume Patient as a separate resource but rather, part of the message
itself. This is the same for other resources included in the resource like address, location etc.

* **Creating an event:** Add the entire message in an attribute so it can be retrieved. This attribute has the entire
  original message with no changes. The event-id must be contained in the message itself. Our backend won't create the
  id.
* **Retrieve an event:** The simplest form is by id; `GET /event/{id}`. This access pattern should always result in
  either one resource or none
* **Search:** This pattern can be broken down into two main categories. The first pattern assumes a known Patient id
  and, the second one filters events based on search criteria.
    * We have a *Global Secondary Index* which has `nhsNumber` and a `sort-key` based on patient's `dateOfBirth`. This
      means, searching for a specific patient must contain at least the `nhsNumber`. Otherwise, we need to perform a
      scan which is not ideal. **So, in any search endpoint we always assume `nhsNumber` is a required query-parameter.
      **
    * `/event?NhsNumber=1234567,dateOfBirth=01/01/1970,diseaseTypeFilter=covid|flu|mmr|hpv|polio`
      The NhsNumber in the above endpoint is required. The dateOfBirth has been used as sort-key.

### Field mappings

Given the relational model (below image) and `sample_event.json` below is our field mappings for highlighted fields:
![img](img/relational-model.png)

* `UNIQUE_ID -> $["identifier"][0]["value"]`
* `UNIQUE_ID_URI -> $["identifier"][0]["system"]`
* `ACTION_FLAG -> ?????`
* `VACCINATION_PROCEDURE_CODE -> $["extension"][0]["valueCodeableConcept"]["coding"][0]["code"]`
* `VACCINATION_PRODUCT_CODE -> $["vaccineCode"]["coding"][0]["code"]`
* `DISEASE_TYPE -> $["protocolApplied"][0]["targetDisease"][0]["coding"][0]["code"]`
* `LOCAL_PATIENT_ID -> $["contained"][0]["item"][3]["answer"][0]["valueCoding"]["code"]`
* `LOCAL_PATIENT_TYPE_URI -> $["contained"][0]["item"][3]["answer"][0]["valueCoding"]["system"]`

TODO: write the rest of the mappings.

**Q**: What does this
mean: [[first point in Overview]](https://nhsd-confluence.digital.nhs.uk/display/Vacc/Immunisation+FHIR+API+-+IEDS+Data+Model)
> This data model must include backwards compatibility with the legacy CSV process to account for business continuity

## Error Scenarios

We assume all error responses will be of type `OperationOutcome`. We can break down scenarios in three categories. One
group is errors that are generated and dealt with in the Proxy before reaching to our backend.
Authentication/authorisation errors belong to this group.

A second group is related to both fine and coarse validation errors.

* **Q:** What is expected in the response message? A detailed diagnostics of the validation or just a generic error?

The third group is anything related to the backend itself. `404` and, catch-all exceptions in the source code (like
malformed json for example)
