# Evidence Scenario

## Scenario

- Project: `<Project>`
- Scenario folder: `.agent/projects/<Project>/evidence/YYYY-MM-DD-scenario/`
- Site / environment: `<production | staging | local>`
- Consent path: `<accept | reject | mixed | not tested>`
- Browser profile: `<Chrome profile or CDP profile>`
- Date/time: `<YYYY-MM-DD HH:mm>`

## Artifacts

- Scenario manifest: `scenario.json`
- Recorder JSON: `<filename>`
- Recorder raw pushes: `<filename or not exported>`
- Recorder network analytics records: `<present | not observed | not supported>`
- HAR: `<filename>`
- CDP comparison JSON: `<filename or not run>`
- CDP comparison MD: `<filename or not run>`
- GTM export used for comparison: `<filename>`

## scenario.json Fields

- site: `<site>`
- environment: `<production | staging | local>`
- consentPath: `<accept | reject | mixed | not tested>`
- chromeProfile: `<profile label>`
- recorderVersion: `<version>`
- expectedDataSource: `<spec | GTM export | live GTM MCP | project notes | none>`
- artifacts: `<filenames>`

## Journey Steps

- [ ] home page load
- [ ] category / PLP
- [ ] search results
- [ ] real product click
- [ ] PDP load
- [ ] related / upsell product click
- [ ] add to cart
- [ ] cart
- [ ] checkout entry
- [ ] checkout success, staging/test only

## Operator Notes

- What was clicked:
- What looked unexpected:
- Known limits of this run:
- Follow-up needed:
