# Staging password protection acceptance

## First hosted deployment — 8 November 2026

- Source: `8f2dc92f15639c836c0684d312554c42b6f8f125` (PR #28).
- Staging artifact: `21e34b10323985b19fa2b97a192033f302f710ab`.
- cPanel deployment 60 succeeded; the private source marker matched.
- Anonymous HTTPS requests to home, contact, CSS, logo, robots, the enquiry
  endpoint (GET only) and a missing page returned 401 with the staging login
  challenge and no application session cookie. The provider returned a generic
  `401 Unauthorized` body with no application content.
- Plain HTTP home/contact/API requests returned 403 without a password prompt.
- Access to `.htaccess` returned 403.
- The owner confirmed Melanie's staging login works after activation.
- No enquiry was submitted or email sent during these checks.
- Production remained on artifact `9cbda3ea3ce4122d412a27ba90d6dcbe705e13a8`,
  deployment 59. Production home/contact returned 200; contact reported PHP
  `8.3.36`. No production or PHP configuration was changed.

## Repeat deployment preparation

This documentation-only revision supplies a new source SHA for a subsequent
staging release. The release process intentionally refuses to overwrite an
existing source-SHA release directory; simply rebuilding the first source SHA
would not provide a valid repeat-deployment test.

Website content, application code, deployment logic, credentials and PHP
settings are unchanged. Use the normal PR/check/merge workflow to generate the
next `deploy-staging` artifact, then obtain separate checkout-update and
activation approvals. Do not rebuild or activate production.

After the next staging deployment:

1. Verify the cPanel task and private source marker match the new release.
2. Repeat anonymous HTTPS and HTTP checks for pages, assets and the API, without
   sending an enquiry. Confirm no session cookie or application output leaks.
3. Ask the owner to confirm Melanie can still log in and navigate the site.
4. Verify production is unchanged and remains public; do not alter PHP.
5. Record results here before declaring hosted deployment persistence proven.

Status: first hosted activation and owner login confirmed; repeat hosted
deployment and its post-deployment acceptance remain pending.
