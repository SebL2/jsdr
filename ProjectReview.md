# Project Review

## What We Completed
- Wired one security feature from `security/security.py` into `server/endpoints.py`.
- Added policy enforcement for one endpoint:
  - `POST /auth/me/favorites`
- Enforced `people -> create` policy using:
  - `checks.login`
  - `user_list` allowlist (email-based)
- Kept `security/security.py` unchanged, per request.

## Current Behavior (As Implemented)
- User must be authenticated.
- If `people.create.checks.login` is true, request requires authenticated user email.
- If `people.create.user_list` is non-empty, email must be included or request is denied (`403`).
- If `people` or `create` policy is missing, route remains open to authenticated users.

## Files Touched
- `server/endpoints.py`

## Validation Checklist
- [ ] Logged-in allowlisted user can add favorites (expect `200`).
- [ ] Logged-in non-allowlisted user is denied (expect `403`).
- [ ] Logged-out user is denied (expect `401`).
- [ ] Existing favorites behavior still works for allowed users.
- [ ] No unrelated endpoint regressions.

## Risks / Gaps
- `security/security.py` is still primarily a policy storage/lookup module.
- Policy is wired to only one route so far.
- Policy loading path and schema consistency should be reviewed before broader rollout.

## Next Steps
- Decide which additional routes should use the same policy checks.
- Add endpoint tests for allowlist/login policy behavior.
- Optionally introduce a shared helper/decorator for policy-enforced endpoints.

## Notes
- Include links to relevant PRs, commits, and test evidence here.
