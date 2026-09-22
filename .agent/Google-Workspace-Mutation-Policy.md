# Google Workspace Mutation Policy

- Gmail: draft-first; direct send only on explicit user instruction; reads require a workspace Gmail access scope.
- Drive: diff-before-share; show permission changes before mutation.
- Calendar: read-before-write; require exact timezone and event details.
- GTM: read-before-write; publish remains separately gated.
- Docs: preview-before-write; identify document and insertion target.
- Sheets: preview-before-write; identify spreadsheet, sheet, and range.
