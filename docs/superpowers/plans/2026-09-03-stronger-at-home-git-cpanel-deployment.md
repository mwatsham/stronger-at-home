# Stronger at Home Git and cPanel Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Add Git-controlled staging and production pipelines that build traceable deployment branches automatically and activate each release through a separate, reviewed cPanel action.

**Architecture:** The develop branch produces deploy-staging; an approved production workflow from main produces deploy-production. Each generated branch contains an environment-specific public tree, private dependency tree, cPanel deployment instructions and source-SHA metadata. cPanel pulls those branches from GitHub, and an operator deliberately starts each cPanel deployment through the guarded integration.

**Tech Stack:** Git and GitHub Actions, Python 3.14 standard library, PHP 8.4, Composer 2 with PHPMailer 7.1.1, Bash, cPanel Git Version Control and the reviewed cpanel-integration CLI.

**Spec:** docs/superpowers/specs/2026-09-03-stronger-at-home-git-cpanel-deployment-design.md

## Global Constraints

- Read AGENTS.md, the specification above, docs/website-staging-runbook.md, scripts/package_site.py, scripts/validate_site.py and tests/test_site_package.py before editing.
- Treat every file under sources/ as read-only reference material.
- Preserve the user's staged AGENTS.md and unrelated untracked .DS_Store, apply_pdf_background.py and build_invoice_template.py.
- Use an isolated worktree created with superpowers:using-git-worktrees for implementation.
- develop is the only source for deploy-staging; main is the only source for deploy-production.
- Generated deployment branches must never be edited manually.
- GitHub may use its repository-scoped token to update deployment branches, but it must not store or receive a cPanel SSH key, cPanel API token, mail password, Fernet key or protected cPanel profile.
- The exact cPanel account home is /home/v0398ees6dry.
- The staging document root is /home/v0398ees6dry/public_html/staging.stronger-at-home.co.uk.
- The production document root is /home/v0398ees6dry/public_html/stronger-at-home.co.uk.
- The staging external configuration is /home/v0398ees6dry/private/stronger-at-home/staging/site.php.
- The production external configuration is /home/v0398ees6dry/private/stronger-at-home/production/site.php.
- Keep the staging and production Composer dependency trees separate and outside both public document roots.
- Staging uses a safe test recipient and must never deliver to Melanie's live address.
- Production activation remains blocked until the portrait, privacy wording, production configuration and delivery test are explicitly approved.
- Do not create, update or deploy a cPanel repository without a fresh read-only inspection, reviewed dry run and operation-bound confirmation.
- Do not push, change GitHub settings or mutate cPanel before the implementation review checkpoint.
- Commit after every code task, run git diff --check before every commit, and stage only files named by that task.

## File Structure

- site/api/enquiry.php — load an explicitly configured autoloader and site configuration from paths outside the public root.
- tests/php/EnquiryEndpointTest.php — prove external autoloader validation and existing environment safeguards.
- scripts/build_git_release.py — convert the approved deterministic package into one environment-specific deployment tree.
- tests/test_git_release.py — verify metadata, environment isolation, forbidden-file boundaries and reversible deployment behaviour.
- .github/workflows/ci.yml — run the complete validation suite for branches and pull requests.
- .github/workflows/release-staging.yml — build develop and promote its artifact to deploy-staging.
- .github/workflows/release-production.yml — build approved main and promote its artifact to deploy-production.
- tests/test_git_release_workflows.py — enforce branch, permission, approval and credential boundaries.
- docs/website-staging-runbook.md — replace manual ZIP activation with the reviewed staging Git lifecycle.
- docs/website-production-runbook.md — define gated production deployment and rollback.
- tests/test_staging_runbook.py and tests/test_production_runbook.py — keep both runbooks aligned with the approved design.

---

### Task 1: Isolate Composer dependencies per environment

**Files:**
- Modify: site/api/enquiry.php:11-31
- Modify: tests/php/EnquiryEndpointTest.php:15-55
- Modify: scripts/validate_site.py approved public-source hash for site/api/enquiry.php

**Interfaces:**
- Consumes: STRONGER_HOME_AUTOLOAD and STRONGER_HOME_CONFIG, both absolute paths supplied by environment-specific Apache configuration.
- Produces: generic HTTP 500 before application startup when either path is missing, unreadable or inside the public root.

- [ ] **Step 1: Write the failing external-autoloader tests**

Extend endpoint_status() so the isolated runner sets both environment variables. Add cases for a missing autoloader and for an autoloader created under site/api/. Both must return a blank generic 500.

~~~php
putenv('STRONGER_HOME_AUTOLOAD=' . $autoloadPath);
putenv('STRONGER_HOME_CONFIG=' . $configPath);
~~~

- [ ] **Step 2: Run the endpoint test and verify failure**

Run: php tests/php/EnquiryEndpointTest.php

Expected: FAIL because site/api/enquiry.php still ignores STRONGER_HOME_AUTOLOAD.

- [ ] **Step 3: Require and validate the configured autoloader**

Replace the shared-directory fallback with:

~~~php
$publicRoot = realpath(dirname(__DIR__));
$autoloadPath = getenv('STRONGER_HOME_AUTOLOAD');
$resolvedAutoloadPath = is_string($autoloadPath) ? realpath($autoloadPath) : false;
if ($publicRoot === false
    || $resolvedAutoloadPath === false
    || !is_file($resolvedAutoloadPath)
    || !is_readable($resolvedAutoloadPath)
    || $resolvedAutoloadPath === $publicRoot
    || str_starts_with($resolvedAutoloadPath, $publicRoot . DIRECTORY_SEPARATOR)
) {
    http_response_code(500);
    exit;
}
require $resolvedAutoloadPath;

$configPath = getenv('STRONGER_HOME_CONFIG');
$resolvedConfigPath = is_string($configPath) ? realpath($configPath) : false;
~~~

Keep the existing configuration, environment, origin, rate-limit and recipient checks. There must be no fallback to public_html/vendor or config/site.php.

- [ ] **Step 4: Refresh the approved hash and run focused tests**

Print the SHA-256 of site/api/enquiry.php, review the complete diff, and replace only its value in APPROVED_PUBLIC_SOURCE_SHA256.

Run:

~~~bash
for test_file in tests/php/*Test.php; do php "$test_file" || exit 1; done
for php_file in $(find site tests/php config -type f -name '*.php' | sort); do php -l "$php_file" || exit 1; done
python -m unittest tests.test_site_validation tests.test_site_package -v
~~~

Expected: all checks pass.

- [ ] **Step 5: Commit**

~~~bash
git add site/api/enquiry.php tests/php/EnquiryEndpointTest.php scripts/validate_site.py
git diff --cached --check
git commit -m "fix: isolate deployment dependencies by environment"
~~~

### Task 2: Build deterministic Git deployment trees

**Files:**
- Create: scripts/build_git_release.py
- Create: tests/test_git_release.py

**Interfaces:**
- Consumes: package_site(project_root: Path, destination: Path, environment: str) -> Path.
- Produces: build_git_release(project_root: Path, output_directory: Path, environment: str, source_sha: str, build_timestamp: str) -> Path.
- Produces: a clean directory containing .cpanel.yml, deploy.sh, release.json, public/ and vendor/.

- [ ] **Step 1: Write failing release-boundary tests**

Create tests that build staging into a temporary directory and require the exact five top-level entries, no symlinks, a 40-character source SHA, build timestamp, develop source branch, deploy-staging deployment branch and staging hostname. Add corresponding production assertions for main, deploy-production and the production hostname.

Add tests requiring staging public/.htaccess to contain:

~~~text
SetEnv STRONGER_HOME_CONFIG "/home/v0398ees6dry/private/stronger-at-home/staging/site.php"
SetEnv STRONGER_HOME_AUTOLOAD "/home/v0398ees6dry/stronger-at-home-releases/staging/0123456789abcdef0123456789abcdef01234567/vendor/autoload.php"
~~~

Require the production output to contain only production equivalents and reject source SHAs such as main, abc and forty non-hexadecimal characters.

- [ ] **Step 2: Run the test and verify the missing-module failure**

Run: python -m unittest tests.test_git_release -v

Expected: ERROR because scripts.build_git_release does not exist.

- [ ] **Step 3: Implement configuration and safe extraction**

Define ACCOUNT_HOME as /home/v0398ees6dry and an immutable ENVIRONMENTS map containing, for each environment, sourceBranch, deploymentBranch, hostname, documentRoot, configPath, repositoryRoot and releaseRoot.

Implement five functions with these exact typed interfaces:

- validate_provenance(source_sha: str, build_timestamp: str) -> None
- extract_approved_archive(archive: Path, destination: Path) -> None
- environment_bindings(environment: str, source_sha: str) -> str
- deployment_script(environment: str, source_sha: str) -> str
- build_git_release(project_root: Path, output_directory: Path, environment: str, source_sha: str, build_timestamp: str) -> Path

validate_provenance() accepts only lowercase forty-character hexadecimal SHAs and UTC timestamps matching YYYY-MM-DDTHH:MM:SSZ. extract_approved_archive() rejects absolute archive names, parent traversal, symlinks and any root other than public/ or vendor/ before writing. Build in a temporary sibling and rename into place only after completion.

Append exactly the two environment bindings to public/.htaccess and reject pre-existing occurrences. Write release.json with sorted keys, two-space indentation and a final newline.

- [ ] **Step 4: Generate guarded cPanel deployment instructions**

Generate:

~~~yaml
---
deployment:
  tasks:
    - /bin/bash deploy.sh
~~~

Generate deploy.sh with literal, reviewed values. It must:

1. enable set -Eeuo pipefail and umask 027;
2. require HOME to equal /home/v0398ees6dry;
3. require pwd -P to equal the environment's cPanel repository root;
4. require public/.htaccess, vendor/autoload.php and the external site.php;
5. reject an existing release directory or next directory for the same source SHA;
6. copy vendor to /home/v0398ees6dry/stronger-at-home-releases/<environment>/<source-sha>/vendor;
7. copy public to a complete next-directory sibling of the document root;
8. move the previous document root under that release directory;
9. move the complete next directory into the exact document-root path;
10. use an EXIT trap to restore the previous directory if the second move fails; and
11. write deployed-source-sha only after the swap succeeds.

Do not add automatic cleanup. Previous releases remain until acceptance and deliberate retention review.

- [ ] **Step 5: Test deployment and recovery in a temporary account home**

Run a test-only copy of the generated script after replacing the literal account-home prefix with a temporary directory. Start with an old document root containing obsolete.txt. After a successful run assert that obsolete.txt is absent from the live root, present in previous-public, the new index exists, the release-specific vendor exists and deployed-source-sha equals the expected SHA.

Add a failure test that makes the second move fail and assert that the old document root is restored. Add a wrong-working-directory test and require a non-zero exit without changing either tree.

Run: python -m unittest tests.test_git_release tests.test_site_package -v

Expected: all tests pass.

- [ ] **Step 6: Add and test the command-line entry point**

Support:

~~~bash
python scripts/build_git_release.py --environment staging --source-sha 0123456789abcdef0123456789abcdef01234567 --build-timestamp 2026-09-03T22:00:00Z --output-directory output/git-release/staging
~~~

The command prints the completed directory and SHA-256 of release.json, returns zero on success and one with a concise error on invalid input. Test the command through subprocess with a temporary output directory.

- [ ] **Step 7: Commit**

~~~bash
git add scripts/build_git_release.py tests/test_git_release.py
git diff --cached --check
git commit -m "feat: build traceable cPanel release trees"
~~~

### Task 3: Add CI and deployment-branch workflows

**Files:**
- Create: .github/workflows/ci.yml
- Create: .github/workflows/release-staging.yml
- Create: .github/workflows/release-production.yml
- Create: tests/test_git_release_workflows.py

**Interfaces:**
- Consumes: build_git_release.py from Task 2.
- Produces: deploy-staging commits from develop and deploy-production commits from an approved main workflow run.

- [ ] **Step 1: Write failing workflow contract tests**

Require:

- CI on pushes to main and develop, pull requests and manual dispatch with contents: read.
- Staging only on develop, contents: write, non-cancelling release-staging concurrency, --environment staging and DEPLOYMENT_BRANCH: deploy-staging.
- Production only through workflow_dispatch, environment: production, checkout ref: main, --environment production and DEPLOYMENT_BRANCH: deploy-production.
- No occurrence of cpanel_token, cpanel_password, fernet, smtp_password, ssh_private_key, appleboy/ssh or scp-action in any workflow.

- [ ] **Step 2: Run the tests and verify missing-file failures**

Run: python -m unittest tests.test_git_release_workflows -v

Expected: ERROR because the workflow files do not exist.

- [ ] **Step 3: Create CI**

Use PHP 8.4, Python 3.14 and Composer caching. Run:

~~~bash
composer install --no-dev --no-interaction --prefer-dist
for test_file in tests/php/*Test.php; do php "$test_file" || exit 1; done
for php_file in $(find site tests/php config -type f -name '*.php' | sort); do php -l "$php_file" || exit 1; done
python -m unittest discover -s tests -q
python scripts/validate_site.py --mode development
python scripts/validate_site.py --mode staging
python scripts/validate_brand.py
node --check site/assets/js/site.js
python scripts/package_site.py --environment staging --destination output/site-package
git diff --exit-code
~~~

Do not attempt production packaging in general CI while approved publication blockers remain.

- [ ] **Step 4: Create automatic staging packaging**

release-staging.yml runs on develop and manual dispatch, but the job proceeds only when github.ref equals refs/heads/develop. Give it contents: write and non-cancelling concurrency. Run the complete CI gate, then:

~~~bash
git fetch --no-tags origin develop
test "${{ github.sha }}" = "$(git rev-parse origin/develop)"
python scripts/build_git_release.py --environment staging --source-sha "${{ github.sha }}" --build-timestamp "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" --output-directory release
~~~

Promote release/ to deploy-staging with a detached Git worktree, the github-actions[bot] identity and a normal fast-forward push. Fetch and track the branch when it exists; otherwise create an orphan branch. Remove all old tracked files, copy release/ contents, commit deploy: stage <source-sha>, push HEAD:refs/heads/deploy-staging, then always remove and prune the temporary worktree.

- [ ] **Step 5: Create gated production packaging**

release-production.yml uses workflow_dispatch only, contents: write, non-cancelling concurrency and a job protected by environment: production. Check out ref: main with full history. Run the complete test suite plus:

~~~bash
python scripts/validate_site.py --mode production
python scripts/package_site.py --environment production --destination output/site-package
git fetch --no-tags origin main
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
~~~

Build with --environment production and promote a clean worktree to deploy-production using commit message deploy: production <source-sha>. The workflow must fail while any production publication gate remains.

- [ ] **Step 6: Verify and commit**

Run:

~~~bash
python -m unittest tests.test_git_release_workflows -v
python -m unittest discover -s tests -q
for test_file in tests/php/*Test.php; do php "$test_file" || exit 1; done
git diff --check
~~~

Expected: all checks pass.

Commit:

~~~bash
git add .github/workflows tests/test_git_release_workflows.py
git diff --cached --check
git commit -m "ci: prepare staging and production release branches"
~~~

### Task 4: Replace manual upload instructions with Git runbooks

**Files:**
- Modify: docs/website-staging-runbook.md
- Modify: tests/test_staging_runbook.py
- Create: docs/website-production-runbook.md
- Create: tests/test_production_runbook.py

**Interfaces:**
- Consumes: generated deployment branches and reviewed cPanel runtime commands.
- Produces: exact preflight, deployment, verification and rollback procedures for both environments.

- [ ] **Step 1: Write failing runbook tests**

Require the staging runbook to contain deploy-staging, repositories/stronger-at-home-staging, runtime version-control, runtime git-update, runtime deployment-create and runtime deployments. Require it to omit files upload and File Manager archive extraction.

Require the production runbook to contain deploy-production, the exact production repository and document roots, GitHub production approval, the production external configuration, live-recipient confirmation, deployment status and rollback verification.

- [ ] **Step 2: Run and verify failure**

Run: python -m unittest tests.test_staging_runbook tests.test_production_runbook -v

Expected: FAIL because staging still documents ZIP upload and the production runbook is absent.

- [ ] **Step 3: Rewrite the staging deployment sections**

Retain relevant runtime, secret-file and staging smoke checks. Replace ZIP upload and manual directory swaps with this exact lifecycle:

1. verify deploy-staging and read release.json;
2. inspect runtime version-control and runtime deployments;
3. dry-run and confirm git-update for the exact staging repository and branch;
4. verify the checked-out identifier;
5. dry-run and confirm deployment-create;
6. verify successful task status and deployed-source-sha; and
7. run HTTPS, deny-all robots, X-Robots-Tag, security-header, route, asset, accessibility and safe-recipient form tests.

Document the protected approval evidence. This records the reviewed source and branch for the operator; it is not a cPanel runtime descriptor:

~~~json
{
  "url": "git@github.com:mwatsham/stronger-at-home.git",
  "branch": "deploy-staging"
}
~~~

- [ ] **Step 4: Write the production runbook**

Mirror staging with deploy-production and /home/v0398ees6dry/repositories/stronger-at-home-production. Before any mutation require accepted staging, green main, GitHub production approval, final portrait, privacy approval, owner-only production configuration, recipient exactly melanie@stronger-at-home.co.uk, no staging directives in the artifact and explicit first-publication approval.

Production smoke checks cover canonical bare/www HTTPS, absence of noindex, all routes/assets, inaccessible external configuration and vendor paths, generic failure behaviour and one explicitly authorised message to Melanie.

- [ ] **Step 5: Define rollback and commit**

Both runbooks define rollback as a new source commit, regenerated deployment branch, reviewed git-update, reviewed deployment-create and complete smoke checks. State that git-delete, deployment-delete and deleting document-root files are not rollback mechanisms.

Run:

~~~bash
python -m unittest tests.test_staging_runbook tests.test_production_runbook -v
python -m unittest discover -s tests -q
git diff --check
~~~

Commit:

~~~bash
git add docs/website-staging-runbook.md docs/website-production-runbook.md tests/test_staging_runbook.py tests/test_production_runbook.py
git diff --cached --check
git commit -m "docs: define guarded Git deployment operations"
~~~

### Task 5: Review, bootstrap Git and prepare staging

**Files:**
- No source changes expected.
- Create outside Git: owner-readable staging approval evidence, git-create descriptor and git-update descriptor.

**Interfaces:**
- Consumes: reviewed Tasks 1–4.
- Produces: remote main, develop, generated deploy-staging and a cPanel staging mapping ready for separate deployment approval.

- [ ] **Step 1: Run the complete release gate**

Run the PHP tests and syntax checks, all Python tests, development and staging validators, brand validation, JavaScript syntax check, staging release build and git diff --check. Production packaging remains excluded while publication blockers remain.

- [ ] **Step 2: Request independent code review**

Use superpowers:requesting-code-review. Require confirmation that the implementation covers the deployment specification, preserves existing security/content gates and introduces no cPanel credential into GitHub. Resolve findings and rerun Step 1.

- [ ] **Step 3: Inspect the remote**

Run:

~~~bash
git status --short --branch
git remote -v
git ls-remote --heads origin
~~~

Require a clean reviewed implementation branch, origin at git@github.com:mwatsham/stronger-at-home.git and no unexpected remote branch.

- [ ] **Step 4: Integrate and bootstrap main and develop**

Use superpowers:finishing-a-development-branch without including unrelated files. After explicit push approval:

~~~bash
git push origin main
git branch develop main
git push origin develop
~~~

Do not force-push. Wait for CI and the staging workflow. Require deploy-staging/release.json to reference the develop tip.

- [ ] **Step 5: Configure GitHub protections**

Protect main and develop from force pushes and deletion, require CI before merges, create an environment named production, add the project sponsor as required reviewer and prevent self-review when available. Do not add cPanel or mail secrets.

- [ ] **Step 6: Inspect cPanel without mutation**

Run domains inspect for staging.stronger-at-home.co.uk, runtime version-control and runtime deployments with profile test-123reg and the protected audit file. Require the exact document root, no conflicting Stronger@Home mapping and the Fabratory mapping unchanged.

- [ ] **Step 7: Dry-run, create and select the staging repository mapping**

Create three owner-readable operator files outside the project and public document root. They must contain no credentials, must be mode 0600 and must never be committed.

The source-and-branch approval evidence at `/exact/operator/path/stronger-at-home-staging-approval.json` is:

~~~json
{
  "url": "git@github.com:mwatsham/stronger-at-home.git",
  "branch": "deploy-staging"
}
~~~

The git-create descriptor at `/exact/operator/path/stronger-at-home-staging-create.json` is:

~~~json
{
  "url": "git@github.com:mwatsham/stronger-at-home.git",
  "remote_name": "origin"
}
~~~

The git-update descriptor at `/exact/operator/path/stronger-at-home-staging-update.json` is:

~~~json
{
  "remote_name": "origin"
}
~~~

The approval evidence is not passed to `cpanel-admin`. Dry-run creation with the operation-specific git-create descriptor:

~~~bash
cpanel-admin --profile test-123reg --audit-file /private/tmp/sah-cpanel-audit.jsonl --pretty runtime git-create --name stronger-at-home-staging --repository-root /home/v0398ees6dry/repositories/stronger-at-home-staging --source-repository /exact/operator/path/stronger-at-home-staging-create.json --type git --dry-run
~~~

At execution, replace /exact/operator/path with the reviewed owner-readable location. Review the returned target, branch, remote, impact, recovery, digest and expiry. With explicit approval, repeat the identical command with its --confirm and --expires-at values. Any changed preflight requires a new dry run.

After the mapping exists, use a new dry-run to select the approved branch explicitly with the remote-name-only git-update descriptor:

~~~bash
cpanel-admin --profile test-123reg --audit-file /private/tmp/sah-cpanel-audit.jsonl --pretty runtime git-update --name stronger-at-home-staging --repository-root /home/v0398ees6dry/repositories/stronger-at-home-staging --branch deploy-staging --source-repository /exact/operator/path/stronger-at-home-staging-update.json --dry-run
~~~

Review and confirm this as a separate operation with its own fresh digest and expiry. Verify the remote and selected branch with runtime version-control.

- [ ] **Step 8: Stop at staging activation**

After runtime version-control proves the mapping uses origin and selects deploy-staging, report the exact source and deployment SHAs, document root, configuration path and recovery behaviour. Do not run deployment-create without separate staging activation approval.

### Task 6: Activate and accept staging

**Files:**
- No source changes expected.

**Interfaces:**
- Consumes: approved staging mapping and deployment SHA.
- Produces: verified staging acceptance eligible for production promotion.

- [ ] **Step 1: Dry-run and confirm git-update**

Use runtime git-update for the exact staging repository, `--branch deploy-staging` and the protected remote-name-only `/exact/operator/path/stronger-at-home-staging-update.json` descriptor. Review and execute only with its unexpired operation-bound confirmation. Verify the cPanel checkout equals the reviewed deployment commit.

- [ ] **Step 2: Dry-run and confirm deployment-create**

Use runtime deployment-create for /home/v0398ees6dry/repositories/stronger-at-home-staging. Review and execute with its separate confirmation. Poll runtime deployments until success or failure; never start a second task while one is active.

- [ ] **Step 3: Run staging verification**

Follow every check in docs/website-staging-runbook.md: HTTPS, deny-all robots, noindex header, security headers, all routes/assets, inaccessible private paths, responsive/accessibility checks and synthetic safe-recipient enquiry delivery. Record only non-sensitive evidence.

- [ ] **Step 4: Accept or roll back**

On success record source SHA, deployment SHA, cPanel deployment ID and acceptance time. On failure stop production and execute the Git rollback procedure; do not patch the staging document root manually.

### Task 7: Prepare and activate production after publication approval

**Files:**
- No deployment-tooling changes expected.
- Create outside Git: owner-readable production approval evidence, git-create descriptor and git-update descriptor.

**Interfaces:**
- Consumes: accepted staging SHA, approved public content, production configuration and protected GitHub production environment.
- Produces: deploy-production, a separate cPanel production mapping and a verified public release.

- [ ] **Step 1: Prove production prerequisites**

Require recorded portrait and privacy approval. Through the separately approved content workflow, remove those publication blockers and run production validation and packaging. Verify the owner-only production site.php exists, names environment production, uses https://stronger-at-home.co.uk and routes only to melanie@stronger-at-home.co.uk without printing its values.

- [ ] **Step 2: Promote accepted source to main**

Approve a develop-to-main pull request. Require CI success and confirm main contains the accepted staging source plus only approved production-content changes.

- [ ] **Step 3: Generate deploy-production**

Dispatch Release production, approve the GitHub production environment gate and require success. Verify release.json references the current approved main SHA and the artifact has no staging hostname, staging configuration path, deny-all robots replacement or X-Robots-Tag noindex directive.

- [ ] **Step 4: Create and select the production cPanel mapping**

Create the source-and-branch approval evidence at `/exact/operator/path/stronger-at-home-production-approval.json`:

~~~json
{
  "url": "git@github.com:mwatsham/stronger-at-home.git",
  "branch": "deploy-production"
}
~~~

Create the operation-specific git-create descriptor at `/exact/operator/path/stronger-at-home-production-create.json`:

~~~json
{
  "url": "git@github.com:mwatsham/stronger-at-home.git",
  "remote_name": "origin"
}
~~~

Create the remote-name-only git-update descriptor at `/exact/operator/path/stronger-at-home-production-update.json`:

~~~json
{
  "remote_name": "origin"
}
~~~

All three files must be owner-readable mode 0600, outside Git and the public document root, and contain no credentials. The approval evidence is not passed to `cpanel-admin`.

After read-only conflict checks, dry-run creation with the git-create descriptor:

~~~bash
cpanel-admin --profile test-123reg --audit-file /private/tmp/sah-cpanel-audit.jsonl --pretty runtime git-create --name stronger-at-home-production --repository-root /home/v0398ees6dry/repositories/stronger-at-home-production --source-repository /exact/operator/path/stronger-at-home-production-create.json --type git --dry-run
~~~

Review and execute only with its exact unexpired confirmation and explicit production approval. Then select the approved production branch in a separate dry-run using the git-update descriptor:

~~~bash
cpanel-admin --profile test-123reg --audit-file /private/tmp/sah-cpanel-audit.jsonl --pretty runtime git-update --name stronger-at-home-production --repository-root /home/v0398ees6dry/repositories/stronger-at-home-production --branch deploy-production --source-repository /exact/operator/path/stronger-at-home-production-update.json --dry-run
~~~

Review and execute only with a new exact unexpired confirmation, then verify origin and deploy-production with runtime version-control.

- [ ] **Step 5: Update and deploy with separate confirmations**

For later releases, dry-run, review and confirm production git-update with the same protected remote-name-only update descriptor and explicit `--branch deploy-production`; verify the checkout; then separately dry-run, review and confirm deployment-create. Never reuse a confirmation digest.

- [ ] **Step 6: Verify production or roll back**

Follow docs/website-production-runbook.md. Require canonical HTTPS, no staging index controls, all routes/assets, inaccessible private paths, correct production form behaviour and one authorised message to Melanie. On any failure execute the traceable rollback flow and preserve evidence without patient data or credentials.

## Plan Self-Review

- Spec coverage: branch flow, artifacts, separate mappings, external configuration, credential boundaries, staging migration, production approval, verification, rollback and deferred full automation are covered by Tasks 1–7.
- Placeholder scan: cPanel confirmation digests and expiry values must come from fresh dry runs and therefore cannot be stored here. Operator approval and descriptor locations are resolved only in the authorised environment and never committed.
- Interface consistency: build_git_release() and its CLI are defined in Task 2 and consumed unchanged by workflows and release gates. Approval evidence records the reviewed URL and branch; git-create receives URL and remote name; git-update receives the remote name while the branch remains an explicit command argument.
- Scope boundary: portrait and privacy content approval remain hard prerequisites for Task 7 and are not invented by this deployment plan.
