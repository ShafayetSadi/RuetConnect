# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog. Versioning will be introduced later; for now, changes are grouped by date.

## [Unreleased] - 2025-08-12

### Added
- Organization management based on roles and memberships
  - Role helpers in `apps/campus/permissions.py` (`is_org_member`, `is_org_staff`).
  - Member count auto-updates via signals in `apps/campus/signals.py`.
  - Member management views in `apps/campus/views_members.py`:
    - `orgs/<slug>/manage/members/` (list)
    - `orgs/<slug>/manage/members/<int:membership_id>/` (edit role/status)
  - Templates: `templates/campus/org_members.html`, `templates/campus/org_membership_form.html`.
- Organization creation flow
  - Create/edit/list/detail views and forms.
  - Creator auto-added as `admin` member; `member_count` initialized.
  - Templates: `templates/campus/organization_form.html`, `organization_detail.html`, `organization_list.html`.
- Voting and saved-posts endpoints
  - JSON voting endpoint (`v/vote/`) and toggle save (`v/save/<slug>/`).
  - HTMX-based vote UI for posts and comments.
- Dynamic sidebars
  - Left: active “Home/Popular/All” links, RECENT threads, Create Thread/Organization buttons.
  - Right: “Recent Posts” and “Popular Posts” via inclusion tags.
  - New templatetags: `apps/campus/templatetags/campus_sidebar.py`.
- Thread membership & access control
  - `ThreadMembership` model; join flow at `r/<thread_slug>/join/`.
  - Thread detail access requires active org membership AND thread membership.
  - Templates: `templates/threads/thread_join.html`, `thread_join_required.html`.
- Forms
  - `apps/posts/forms.py`, `apps/threads/forms.py`, `apps/campus/forms.py`.
- Admin improvements for posts, threads, comments, and campus organizations.

### Changed
- Consolidated `apps/posts/models.py` to a single `Post` model using `BaseModel`.
  - Robust unique slug generation on create/update.
- Refactored `apps/threads/models.py` to modern fields
  - `title`/`slug`/`created_by`, organization FK, pin/lock flags, indexes.
- Views
  - Permissions tightened with `UserPassesTestMixin` and role checks for thread/org editing.
  - Post create now requires org + thread membership.
  - Home page: added tab sorting (Home/Popular/All); Popular prioritizes upvotes, views, comments.
- Templates
  - Replaced `date_posted`/`owner`/`name` with `created_at`/`created_by`/`title`.
  - Fixed URLs to use `slug` and `thread_name` parameters consistently.
  - Avatars updated to `profile.avatar` with fallback images.

### Fixed
- Template library discovery for `campus_sidebar` (added `__init__.py` and builtins registration).
- Template syntax errors (conditional class rendering for tabs).
- Idempotent org join flow; prevents duplicate membership IntegrityError.

### Removed
- Duplicate `Post` class definition and obsolete, conflicting post migrations.

### Breaking changes / Notes
- Thread access is now gated:
  - Users must be active members of an Organization to join/use its Threads.
  - Users must also join a Thread to view/use it.
- Thread model fields changed (`name` -> `title`, `owner` -> `created_by`). Adjust any code or templates referencing old fields.
- Voting endpoints expect POST with `model`, `object_id`, and `action` (`up`/`down`/`clear`).

### Migration & setup
- Run database migrations:
  ```bash
  uv run python manage.py makemigrations
  uv run python manage.py migrate
  ```
- If you have existing data:
  - Backfill `threads.slug` and `threads.created_by` as needed.
  - Ensure users have `OrganizationMembership` before granting `ThreadMembership`.

### URLs overview
- Campus / Organizations
  - `orgs/` (list), `orgs/create/`, `orgs/<slug>/`, `orgs/<slug>/edit/`
  - `orgs/<slug>/join/` (request to join)
  - `orgs/<slug>/manage/members/` and `.../<int:membership_id>/` (role/status)
- Threads
  - `r/create/`, `r/<thread_slug>/`, `r/<thread_slug>/join/`, `r/<thread_slug>/update/`
- Posts
  - `post/create/`, `post/<slug>/`, `post/<slug>/update/`, `post/<slug>/delete/`
- Votes
  - `v/vote/`, `v/save/<slug>/`

---

If anything is unclear or you need a data migration script for existing installations, open an issue and we’ll add one.
