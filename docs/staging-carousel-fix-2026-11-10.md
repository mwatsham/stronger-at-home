# Staging carousel authentication fix

## Release

- Approved scope: fix same-origin feed credentials and retest staging; preserve quotes and password protection; production unchanged.
- PR #40 merged into develop: `dd902d69abab5d6af3d6d1f56ac2dbfb9454e30b`.
- PR CI `42899431241`, develop CI `42899682936`, staging build `42899682721`: succeeded.
- Verified deploy-staging artifact: `c1b51c0ec4966ffafc449da643b066202739f334`.
- Guarded cPanel deployment 69: succeeded, task `00000000/6af3850d311bd2`.

## Verification

- Regression test failed with omitted credentials and passed with same-origin credentials. Eight JavaScript tests, 231 Python tests and PHP tests passed. Staging source and brand validation passed; independent review found no blockers.
- Authenticated browser displayed all six existing published quotes after refreshing cached assets. Automatic advancement observed; Next and Previous changed quotes and manual navigation switched the control to Play.
- Private quote-store SHA-256 before and after deployment was identical: `621a6a501dc248057f2800b81353dc5fef98d8fc8e180c67397be4d48c479d8a`.
- No quotes were modified during this retest. The previously labelled test quote remains unpublished.
- Anonymous staging home and feed requests returned HTTP 401 with valid TLS; password protection retained.
- Production home returned HTTP 200 with valid TLS. Production checkout and last successful deployment remained `adfc4ad859404291ec89898ec7131ab956a8498c` / deployment 67.
- No enquiry sent; no production or PHP changes made.

If an already-open browser retains the old script, perform a hard refresh.
