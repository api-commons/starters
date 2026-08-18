# Starters

The smallest correct version of each artifact in the [API Commons](https://apicommons.org)
stack. Copy one, rename everything, and grow it.

## What's here

| Starter | Spec | What it is |
| --- | --- | --- |
| **[starter-openapi.yml](starter-openapi.yml)** | OpenAPI 3.1 | One resource — list, create, read by id — with RFC 9457 errors |
| **[starter-apis.yml](starter-apis.yml)** | APIs.json 0.22 | One index, one API, and the properties a consumer needs to find their way in |
| **[starter-json-schema.yml](starter-json-schema.yml)** | JSON Schema 2020-12 | An object with typed properties, one constraint, and descriptions on everything |

## Starter, not base

A **starter** is the smallest document that is still correct and worth copying. A
**base** is a full working template for a real domain — the whole error contract,
pagination, conditional writes, merge-patch.

Start here when you are starting something. Start from a base when it already resembles
what you are building:

- [accounts](https://github.com/api-commons/accounts) — the account lifecycle
- [images](https://github.com/api-commons/images) — upload, metadata, renditions
- [videos](https://github.com/api-commons/videos) — upload, transcoding, captions
- [train-travel](https://github.com/api-commons/train-travel) — a realistic worked API
- [problem-details-for-http-apis](https://github.com/api-commons/problem-details-for-http-apis) — errors on their own

## They lint clean, and that is the point

`starter-openapi.yml` returns **zero findings** under both `spectral:oas` and the
[API Commons Problem Details ruleset](https://github.com/api-commons/spectral-problem-details-ruleset).

Whatever you build on top of it starts from zero, so the first warning you ever see is
one you introduced. A starter that ships with warnings teaches you to ignore warnings.

```
spectral lint starter-openapi.yml -r https://raw.githubusercontent.com/api-commons/spectral-problem-details-ruleset/main/problem-details.yaml
```

## Validating

```
pip install jsonschema pyyaml
python3 validate.py
```

The validator checks more than well-formedness:

- **starter-json-schema.yml** is a valid 2020-12 document, **and its own `examples`
  validate against the properties they sit on**. A starter whose examples don't validate
  is worse than no starter.
- **starter-apis.yml** validates against the APIs.json schema, fetched live from
  [apis-json/api-json](https://github.com/apis-json/api-json). Not vendored here — a copy
  would drift from the spec. Drop a `schema_0.22.yml` next to `validate.py` to work
  offline.
- **starter-openapi.yml** is checked for operationIds, descriptions, and — specifically —
  that its `Problem` schema matches RFC 9457 member types. `status` as a string is the
  most common problem-detail defect, and [§3.1](https://www.rfc-editor.org/rfc/rfc9457#section-3.1)
  makes it fail *silently*: a conforming consumer must ignore any member whose value type
  does not match.

## Choices these starters make on purpose

**`additionalProperties` is left unset**, in the JSON Schema and in the OpenAPI `Problem`
schema. Setting it to `false` makes every future field a breaking change for anyone
validating against you, and in a problem detail it forbids the extension members
RFC 9457 §3.2 depends on. Decide that on purpose, not by habit.

**`lastName` is optional.** Plenty of people do not have one. A schema that requires it
is wrong about the world rather than strict.

**401 and 429 carry their headers.** `WWW-Authenticate` on a 401 is required by RFC 9110
§11.6.1, and a problem detail explaining the 401 does not substitute for the challenge.
`Retry-After` on a 429 is what stops a retry storm.

**The APIs.json starter leads with properties.** They are the point of the format — each
one a machine-readable pointer to something a consumer or an agent would otherwise go
hunting for. The full vocabulary is at [apicommons.org/common](https://apicommons.org/common/).

## Adding a starter

Add the file, add a row to the table above, and teach `validate.py` how to check it. The
validator is the contract: a starter nobody validates is a starter that quietly rots.

## License

Two licenses, by kind of thing:

- **Artifacts** — the schemas, rulesets, fixtures, examples and API descriptions — are
  **[CC BY-NC-SA 4.0](LICENSE)** (Attribution–NonCommercial–ShareAlike).
- **Code** — the validator, test harness and packaging — is **[Apache-2.0](LICENSE-CODE)**.

API Commons licenses **artifacts** under CC BY-NC-SA 4.0 and **code** under Apache-2.0.

## Part of API Commons

A machine-readable building block from **[API Commons](https://apicommons.org)** — open specifications and schemas for the APIs you produce and consume. See all building blocks at **[apicommons.org](https://apicommons.org)** and the tools at **[apicommons.org/tools](https://apicommons.org/tools/)**.

**Related building blocks**
- [plans](https://github.com/api-commons/plans) — access plans, tiers, and pricing
- [rate-limits](https://github.com/api-commons/rate-limits) — the quotas an API enforces
- [starters](https://github.com/api-commons/starters) — the smallest correct version of each artifact
