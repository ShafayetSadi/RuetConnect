High-level flow (users → organizations → threads)

• Signup and profile
• Users sign up (allauth), complete profile, optional RUET verification.
• Discover and join organizations
• Browse orgs/ list and orgs/<slug>/ detail.
• Request to join; status starts as pending and is approved by org moderators/admins.
• Create organizations
• Verified users can create an organization (orgs/create/).
• Creator is auto-added as admin; org is now visible and can onboard members.
• Create threads inside organizations
• Org admins/moderators create threads tied to the org (thread type: general, announcement, etc.).
• Threads get a global slug and are browsable at r/<thread_slug>/.
• Post and engage
• Users browse threads, create posts (subject to org/thread posting rules), comment, vote, and save posts.
• Moderate and manage
• Moderators/admins approve members, assign roles, pin/lock threads, and moderate content.

Roles and permissions (minimum)

• Visitor: view public orgs/threads/posts.
• Authenticated user: request membership, post in open threads, comment, vote.
• Member: post/comment in member-only threads; access member-only content.
• Moderator: approve/ban members, create/edit threads, pin/lock threads, remove content.
• Admin: edit org settings, manage roles, all moderator powers.

Membership flow

• Request → Pending → Approved (Active) or Rejected → Inactive/Banned.
• member_count updates on status changes to Active/Inactive/Banned.
• Roles: member, moderator, admin (plus optional president/secretary if needed).

URL structure (concise)

• Organizations
• List: orgs/
• Detail: orgs/<slug>/
• Create: orgs/create/
• Edit: orgs/<slug>/edit/
• Join: orgs/<slug>/join/
• Threads
• Detail: r/<thread_slug>/
• Create: r/create/ (or via org context)
• Update/Delete as needed
• Posts & comments
• Post detail: post/<slug>/
• Post create/update/delete; Comment create under post
• Votes
• JSON POST: v/vote/ with model/post or comment id, action up/down/clear

Ownership and moderation rules

• Organization creator becomes admin.
• Admins delegate moderators.
• Only org staff (mods/admins) create/edit threads; org-wide setting can allow members to create threads if desired.
• Threads can be pinned/locked by mods/admins.
• Posts can be restricted to members-only per org/thread policy.

Recommended defaults

• Only verified users can create organizations.
• Anyone can view; only members can post in member-only threads.
• New orgs start with at least one “General” thread.
• Use select_related/prefetch_related for org→thread→post views; add indexes (already added).
• Implemented UI/Views
• Create Organization: orgs/create/ with form and new templates.
• Organization List/Detail/Edit pages and join flow.
• Thread pages aligned to new title/slug/created_by.
• Voting wired via HTMX to JSON endpoints.
• If you want a stricter policy (e.g., only members can post, or only admins can create threads), say the word and I’ll lock it down.
