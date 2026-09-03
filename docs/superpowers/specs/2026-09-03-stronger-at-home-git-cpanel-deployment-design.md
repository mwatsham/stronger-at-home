# Stronger at Home Git and cPanel deployment design

Status: approved architecture; implementation plan pending

Approval owner: Project sponsor

Approved on: 2026-09-03

## Objective

Control releases of the Stronger at Home Physiotherapy website through Git,
with separate staging and production environments, traceable release commits,
and an explicit human decision before cPanel changes either live document root.

The design follows the safer operating model already proven by the Fabratory
project: GitHub automatically validates, builds and prepares deployment
branches, while cPanel repository updates and deployments remain deliberate
operator actions. GitHub therefore does not need a cPanel SSH key, API token or
hosting-account credential.

## Approved decisions

- `develop` is the integration branch and the source of staging releases.
- `main` is the production-ready branch and the source of production releases.
- GitHub Actions automatically validates and packages releases.
- Generated deployment branches are `deploy-staging` and
  `deploy-production`.
- Deployment branches contain built runtime files rather than editable source.
- Staging and production use separate cPanel Git repository mappings, external
  configuration files and document roots.
- Updating a deployment branch does not itself change a website. An operator
  must explicitly update the corresponding cPanel repository and create its
  deployment task.
- Production requires successful staging acceptance and an explicit production
  approval in addition to the cPanel deployment action.
- A release records the immutable source commit from which it was built.
- Rollback is performed as a new traceable release, not by manually editing
  files in a document root.

## Branch and release flow

### Staging

1. Work is completed on a feature branch and reviewed into `develop`.
2. A push to `develop` starts the staging release workflow.
3. The workflow runs all required validation, tests and production-style build
   checks.
4. The workflow creates a clean staging artifact and commits it to
   `deploy-staging` using the GitHub Actions identity.
5. The operator reviews the workflow result and source SHA.
6. The operator updates the cPanel staging repository to the new
   `deploy-staging` tip.
7. The operator creates the cPanel deployment task.
8. The deployment status and staging hostname are verified before the release
   is accepted.

### Production

1. The accepted `develop` state is reviewed and merged into `main`.
2. All required `main` checks must pass.
3. The production release workflow waits for approval through a protected
   GitHub `production` environment.
4. After approval, the workflow creates a clean production artifact and commits
   it to `deploy-production`.
5. The operator confirms that the artifact source SHA matches the approved
   `main` commit.
6. The operator explicitly updates the cPanel production repository and creates
   its deployment task.
7. The production hostname, enquiry path and essential assets are smoke-tested.

The GitHub environment approval controls artifact promotion. The separate
cPanel action is a second safeguard against an accidental public release.

## Repository layout

The source repository remains:

`git@github.com:mwatsham/stronger-at-home.git`

The planned cPanel mappings are:

| Environment | Deployment branch | cPanel repository root | Document root |
| --- | --- | --- | --- |
| Staging | `deploy-staging` | `/home/v0398ees6dry/repositories/stronger-at-home-staging` | `/home/v0398ees6dry/public_html/staging.stronger-at-home.co.uk` |
| Production | `deploy-production` | `/home/v0398ees6dry/repositories/stronger-at-home-production` | `/home/v0398ees6dry/public_html/stronger-at-home.co.uk` |

Repository roots must remain outside public document roots. The implementation
must inspect existing cPanel mappings before creating either repository and
must stop if an unexpected mapping or path conflict exists.

## Deployment artifacts

Each generated deployment branch contains only the files required to run the
selected environment:

- the built public website under `public/`;
- locked PHP dependencies under `vendor/` when required;
- an environment-specific `.cpanel.yml`;
- `release.json`; and
- any other runtime file explicitly approved by the implementation plan.

Editable source, tests, development dependencies, local tooling, credentials
and private configuration are excluded. Deployment branches are generated and
must never be edited by hand.

`release.json` records at least:

- environment name;
- source branch;
- source commit SHA;
- build timestamp; and
- deployment branch.

The packaging workflow must fail if the source branch moves before packaging
finishes or if the artifact contains forbidden files.

## Environment configuration

Runtime credentials and operational configuration remain outside Git and
outside both public document roots.

The staging configuration is:

`/home/v0398ees6dry/private/stronger-at-home/staging/site.php`

The planned production configuration is:

`/home/v0398ees6dry/private/stronger-at-home/production/site.php`

The environment-specific public `.htaccess` binds the application to the
corresponding external configuration path. A staging build must never reference
the production configuration, and a production build must never reference the
staging configuration.

Staging continues to use a safe test recipient. Production mail delivery to
Melanie is enabled only after the privacy notice, portrait, production
configuration and end-to-end delivery checks have been explicitly approved.

## cPanel deployment behaviour

The generated `.cpanel.yml` for each environment deploys only to its approved
document root. It must use absolute, pre-reviewed targets derived from the
cPanel account home rather than repository-relative assumptions.

Before the implementation selects a file-copy strategy, it must test the
hosting account's supported behaviour. The deployment must avoid:

- exposing `.git`, `.cpanel.yml`, `release.json` or private configuration as
  public website files unless a public release endpoint is separately approved;
- leaving obsolete files from an older release in the document root;
- copying a staging configuration into production;
- making a partially copied release visible; and
- deleting the last accepted release before the new release is verified.

If this cPanel account cannot support an atomic release-directory switch, the
implementation plan must define a guarded backup-and-copy sequence with an
explicit recovery path before any production deployment.

## Credentials and access boundary

cPanel retrieves deployment branches from GitHub through a dedicated GitHub
deploy key or another cPanel-supported read-only repository credential. GitHub
Actions uses the repository-scoped GitHub token only to update the generated
deployment branches.

No cPanel SSH private key, cPanel API token, mail password or protected profile
material is stored in the GitHub repository or GitHub Actions secrets for this
design. cPanel update and deployment operations are run through the reviewed
`cpanel-integration` workflow from an authorised operator environment.

## Verification and failure handling

A release is not complete merely because GitHub produced an artifact or cPanel
reported a successful task. Each deployment requires:

- confirmation that the deployment branch records the expected source SHA;
- successful cPanel deployment-task status;
- an HTTPS response from the intended hostname;
- checks for essential styles, scripts and images;
- confirmation that staging remains excluded from indexing;
- an enquiry-form submission test appropriate to the environment; and
- confirmation that no credential or private configuration is publicly
  retrievable.

Failure at any stage stops promotion. Production is not changed when staging
verification fails.

## Rollback

Rollback is a new audited deployment:

1. identify the last accepted source SHA from `release.json` and Git history;
2. revert the faulty source change or prepare an approved rollback commit;
3. run the full validation and build workflow;
4. create a new deployment-branch commit;
5. explicitly update and deploy the relevant cPanel repository; and
6. repeat all environment verification.

Deleting a cPanel repository mapping or deployment-task record is not a
rollback and must not be used as one.

## Initial migration

The existing manually uploaded staging files remain active until the Git-based
staging path has been configured and a release has passed all checks. The
previously extracted staging package is not treated as a Git release and is not
activated as part of this design.

Implementation proceeds in this order:

1. protect and bootstrap the Git branch model;
2. add and test deterministic release packaging;
3. generate `deploy-staging` from `develop`;
4. configure and verify the staging cPanel repository;
5. deploy and accept staging;
6. add the gated production workflow and production configuration;
7. configure the production cPanel repository; and
8. perform the first production deployment only after all public-content and
   operational approvals are complete.

## Deferred enhancements

Fully automatic cPanel activation is deliberately excluded. It would require a
GitHub-held cPanel credential or a cPanel SSH key with a wider hosting-account
access boundary. That can be reconsidered after the guarded workflow is proven
and an acceptable least-privilege credential model is available.

Automated database migrations, CMS deployment, blue-green hosting, scheduled
releases and automatic rollback are also outside this design.
