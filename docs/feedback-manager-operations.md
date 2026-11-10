# Feedback manager

## Local preview

Run `python scripts/preview_feedback.py --generate-local-password` from the project checkout. Requires PHP with mbstring. The server binds only to 127.0.0.1, defaults to port 58640 and prints links for the homepage and manager.

Username: `melanie`. The generated local-only password is saved in the owner-readable password file whose path the command prints. Do not reuse it for staging or production. Alternatively omit that option to choose a preview password through hidden terminal input, or supply an owner-only file with `--password-file`.

The preview contains explicitly labelled demonstration quotes, not real patient feedback. Enquiry submissions are disabled by the local router. Stop with Ctrl+C. Its temporary private workspace is retained for inspection; remove it when no longer needed. None of these files belong in Git or deployment archives.

## Editing

Open `/feedback/admin/` and sign in as Melanie. Save a draft with quote text, agreed public attribution and order (lower numbers first). Review its quote preview. Confirm permission to publish the exact wording and attribution, then publish.

Any edit, including order changes, returns the quote to draft and requires permission confirmation before republishing. Unpublish removes it from the public feed; delete requires a separate confirmation. Refresh the public page to see changes. Concurrent saves from another tab return a conflict; reload before editing again.

There is no public registration or feedback-submission form. Do not paste original messages, private medical details, email addresses or patient records into quote fields.

## Future hosting setup — not performed for this local-preview task

Each environment needs a separate owner-only (0700) private directory:

- Staging: `/home/v0398ees6dry/private/stronger-at-home/staging/feedback`
- Production: `/home/v0398ees6dry/private/stronger-at-home/production/feedback`

The CLI-only `scripts/setup_feedback.php` takes `--directory`, `--environment`, `--origin` and `--password-stdin`. Supply a unique 16–72-byte password from protected input, never an argument or command history. Melanie chooses her real password privately. This creates a password hash, private sessions directory and empty quote store. No real password or live account was created during development.

The release builder binds `STRONGER_HOME_FEEDBACK_CONFIG` to that environment's private `feedback.php`. The existing enquiry configuration is separate and unchanged. Without valid configuration/storage, the manager and feed fail closed (503); existing public review links still work and the carousel remains hidden.

For password recovery, an authorised operator runs the same setup command with `--rotate`, preserving the directory, environment and origin. Quote data is retained. Existing sessions become invalid when the password hash changes. No email-reset mechanism is installed.

Back up the private store and configuration separately from releases, using restricted access. Restoration requires an explicit operator action; corrupt storage is never silently replaced. Credential rotation does not bypass the 15-minute login throttle.

## Security and accessibility

HTTPS-only on hosted environments; secure, HTTP-only, SameSite Strict admin cookies; separate session namespace and private session directory; 30-minute idle and eight-hour absolute expiry. All admin POSTs require CSRF and matching Origin when present. Login protection permits five failed attempts per 15 minutes across the sole account; this intentionally allows a temporary account-wide lockout rather than distributing attempts across IP addresses.

Feed responses contain only published text, attribution and order, with no-store caching. Drafts, permission flags, IDs, session state and password hashes are not public. A maximum of 100 quotes limits storage.

The public carousel rotates every eight seconds. Hover, keyboard focus and hidden tabs pause it temporarily. Previous/Next stops autoplay until Play is chosen. Reduced motion disables autoplay and hides Play/Pause. Zero quotes hides the carousel; one quote hides rotation controls. Google and Trustpilot links stay available if loading fails.

No existing live site or PHP setting is changed by preparing or running the local preview. Staging activation and production activation require separate approval.
