# Feedback production release — completed

## Approved activation

Production artifact `5f005f3abd5ed85013de2cfd66a8b0951e1ea30d` was activated with explicit owner approval as deployment 71, task `00000000/6af3938b3fce73`; cPanel reports success. HTTPS GET checks for home, contact, feedback admin login and feed returned 200. PHP pages report PHP/8.3.36. The contact form and submit control remain present; no enquiry was submitted, so email delivery was not retested.

The public feed returns six published quotes and excludes the labelled test draft. At release verification, the private quote-store SHA-256 was `621a6a501dc248057f2800b81353dc5fef98d8fc8e180c67397be4d48c479d8a`. Browser inspection verified italic double-quoted styling and automatic advancement from quote 1 to quote 2. No stored quotes or PHP settings changed. The owner subsequently confirmed that Melanie can log in to the production feedback manager. Production acceptance is complete.

The preparation entries below are historical; deployment 71 supersedes their unactivated status.

- PR #42 CI run 42906997248 passed; merged to main at `2b26e53684826a12b61455e52d5a40efcb3ac3d5`.
- Main CI 42907734462 and production build 42907803005 succeeded.
- Verified deploy-production artifact: `5f005f3abd5ed85013de2cfd66a8b0951e1ea30d`.
- Metadata identifies production, stronger-at-home.co.uk, main source above, enquiries enabled and the existing pending-registration exception.
- Production bindings point to the private production configuration. No staging Basic authentication gate; no quote store, passwords or sessions bundled in the artifact.
- Private production feedback and sessions directories are 0700; feedback.php and quotes.json are 0600. Unique production credentials are kept outside Git in protected local storage.
- Staging and production quote stores match SHA-256 `621a6a501dc248057f2800b81353dc5fef98d8fc8e180c67397be4d48c479d8a`: revision 18, six published records and one labelled test draft. IDs, consent, order, text, attribution and publication states preserved.
- Production checkout and live deployment remain `adfc4ad859404291ec89898ec7131ab956a8498c`, deployment 67. Home HTTP 200 with TLS verified. No activation, enquiry submission or PHP change performed.

## Historical preparation gates

### Checkout prepared following explicit approval

The production cPanel checkout was updated to `5f005f3abd5ed85013de2cfd66a8b0951e1ea30d` without activation. Read-back confirmed live deployment remains 67 (`adfc4ad859404291ec89898ec7131ab956a8498c`). Staging and production quote checksums remain identical to the recorded snapshot; production home HTTP 200 with verified TLS. No PHP changes or deployment-create operation performed.

These preparation and activation gates have now been completed. Do not publish the labelled test draft. The migrated snapshot is not ongoing synchronisation between staging and production; future live quote edits belong in the production manager.

## Source branch synchronisation

The owner requested syncing develop with main while preserving both live deployments and PHP. Main is `2b26e53684826a12b61455e52d5a40efcb3ac3d5`; develop is its ancestor, permitting a fast-forward with no source-content changes. The develop push runs CI and prepares a staging artifact only; it does not activate cPanel hosting. Production remains deployment 71 and staging remains deployment 70.
