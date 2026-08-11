# Bot Management System — Problem & Solution Log

---

## 1. Pages / Groups Being Created Twice

**Symptom:** Adding a page or group resulted in a duplicate entry.

**Root Cause:** Both the HTML `onsubmit="..."` attribute AND the JavaScript event listener were wired up simultaneously on `pageForm` and `groupForm`, causing every form submission to fire twice.

**Fix:**

- Removed the inline `onsubmit` attributes from `pageForm` and `groupForm` in `management.html`.
- Kept only the JavaScript event listeners in `management.js`.

---

## 2. Server Error When Adding FAQs

**Symptom:** Submitting the FAQ create form returned a server error.

**Root Cause:** The `faq_create` view used `request.selected_bot` directly when saving — but the `BotSelectionMiddleware` sets this to `None` if no bot is selected, causing an `IntegrityError`.

**Fix (`bot_app/views.py`):**

- Added an explicit check at the start of `faq_create`: if `request.selected_bot` is `None`, return a JSON error immediately instead of crashing.

---

## 3. Server Error on Category Create / List

**Symptom:** Server error when creating or listing categories.

**Root Cause:** The views accessed `request.user.telegram_user.workspace` directly. After the project was refactored from "Pharmacy" to "Workspace", `telegram_user` may not always be present, causing an `AttributeError`.

**Fix (`bot_app/views.py`):**

- Added a `_get_request_workspace(request)` helper function that safely falls back through multiple lookup paths (`telegram_user.workspace`, `request.user.workspace`, POST/GET `workspace_id`).
- Used this helper in `category_create`, `category_list`, and `category_delete`.

---

## 4. Server Error on Category Delete

**Symptom:** Clicking "Confirm Delete" on a category resulted in a server error.

**Root Cause 1:** The workspace ownership check (`cat.workspace != workspace`) crashed when `_get_request_workspace()` returned `None` — comparing a model object to `None` raised a `TypeError`.

**Root Cause 2:** The delete confirm button's event listener was attached before the DOM element had an `id` attribute, so the listener silently failed.

**Fix:**

- Made the workspace check conditional: `if workspace and cat.workspace != workspace`.
- Added `id="pageForm"` to the form element in `management.html` so JavaScript could attach to it correctly.
- Added null-checks to all event listener attachments in `management.js`.

---

## 5. "Error Loading Content" / "Failed to Load Content" on View Tree

**Symptom:** Clicking the View (tree) button for a category showed "Error loading content" or "Failed to load content."

**Multiple Root Causes (fixed in order):**

### 5a. `ecom.Medicine` top-level import crashed all bot_app views

- **Cause:** `from ecom.models import Medicine, Category, Order, OrderItem` was at the **top of `bot_app/views.py`**. On the AWS production database (`bot_management_db`), the `ecom` tables don't exist, so this import failed on module load — meaning **every single bot_app view** returned a 500 before running.
- **Fix:** Removed the top-level import. The only remaining use of `Medicine` (in `get_attachments`) now imports it lazily inside a `try/except` block.

### 5b. `groups__medicines` prefetch queried missing table

- **Cause:** `faq_list_by_category_partial` used `.prefetch_related('groups__medicines')`. The `bot_page_group_medicines` table doesn't exist on AWS.
- **Fix:** Removed the `medicines` prefetch. Wrapped the whole view in a `try/except` that returns a JSON error instead of a 500.

### 5c. `bot_page_group_medicines` table missing — PageGroup.medicines M2M

- **Cause:** The `PageGroup.medicines` ManyToManyField was defined in `0002_initial.py` which depended on `ecom.0001_initial`. Since ecom migrations were never run on `bot_management_db`, migration `0002` was skipped, leaving the join table uncreated.
- **Fix:**
  - Removed `medicines = ManyToManyField('ecom.Medicine', ...)` from `PageGroup` model.
  - Created migration `0006_remove_pagegroup_medicines.py` using `SeparateDatabaseAndState` — it removes the field from Django's model state and conditionally drops the table only if it exists in the DB.
  - Removed all `group.medicines.set()`, `group.medicines.clear()`, and template `group.medicines.all` references.

### 5d. `bot_page_group_attachments` table missing — PageGroup.attachments M2M

- **Cause:** Even though `0001_initial.py` defined `PageGroup.attachments`, this table was also never physically created on the AWS production database (DB state inconsistency from the pharmacy→workspace refactor).
- **Fix:**
  - Removed `attachments = ManyToManyField('core.Attachment', ...)` from `PageGroup` model.
  - Created migration `0007_remove_pagegroup_attachments.py` (same `SeparateDatabaseAndState` pattern — drops table only if it exists).
  - Removed `'groups__attachments'` from the `prefetch_related` in `faq_list_by_category_partial`.
  - Removed all template references in `page_list_item.html`: `group.attachments.all`, `group.attachments.count`, `group.attachments.exists`.

---

## 6. Group Creation — "Field 'id' expected a number but got UUID"

**Symptom:** Creating a group failed with a type error on the attachment ID.

**Root Cause:** The frontend `selectedAttachmentIds` list was originally designed to hold both integer Attachment IDs and UUID Medicine IDs. After medicines were removed, UUIDs were still being sent. The `Attachment` model uses integer PKs, so passing a UUID to `Attachment.objects.filter(id__in=...)` crashed.

**Fix (`bot_app/views.py` — `group_create` and `group_update`):**

- Added a filter: `integer_ids = [aid for aid in attachment_ids if str(aid).isdigit()]`
- Only integer IDs are passed to the `Attachment` queryset.

---

## 7. JS Error Hiding Real Server Messages

**Symptom:** The tree view modal always showed "Failed to load content" or "Error loading content" with no details, making it difficult to debug.

**Fix (`management.js`):**

- Updated the `openViewModal` fetch handler to extract `data.error` from the JSON response and display it in the modal alongside the generic message.
- Updated the network error handler to also show the exception text.

---

## Summary of Key Files Modified

| File                                                      | What Changed                                                                                                                               |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `bot_app/models.py`                                       | Removed `medicines` and `attachments` ManyToManyFields from `PageGroup`                                                                    |
| `bot_app/views.py`                                        | Added `_get_request_workspace()`, lazy `ecom` imports, `try/except` on tree view, fixed `group_create`/`group_update`, removed M2M queries |
| `bot_app/migrations/0006_remove_pagegroup_medicines.py`   | Safe conditional removal of medicines M2M                                                                                                  |
| `bot_app/migrations/0007_remove_pagegroup_attachments.py` | Safe conditional removal of attachments M2M                                                                                                |
| `management.html`                                         | Removed duplicate `onsubmit` handlers, added `id="pageForm"`                                                                               |
| `management.js`                                           | Added null-checks for event listeners, improved error display in tree view                                                                 |
| `page_list_item.html`                                     | Removed all `group.attachments.*` and `group.medicines.*` template references                                                              |
| `bot_app/urls.py`                                         | Added `/dashboard/debug-tables/` and `/dashboard/fix-tables/` debug endpoints                                                              |

---

## 8. Migration from AWS Elastic Beanstalk to Ubuntu VPS (Lightsail)

**Problem / Motivation:**
The original platform was hosted on AWS Elastic Beanstalk combined with AWS RDS (Managed Database) and an Elastic Load Balancer. This architecture was highly scalable but generated monthly fees of ~$53+ even with minimal traffic. The complexity also made deployments slow and opaque.

**Solution Chosen:**
We migrated the entire application to an **AWS Lightsail Ubuntu 24.04 VPS** as a single-node deployment.

- **Cost Reduction:** AWS Lightsail charges a flat, predictable fee of **$5.00/month** (first 90 days are free).
- **Architecture:** We moved from a distributed setup to a monolith. Nginx acts as the reverse proxy, Gunicorn serves the Django app, and a local MySQL server handles the database.

### Steps Taken for Migration:

1. **Server Provisioning:** Launched a single 512MB RAM Lightsail VPS with Ubuntu 24.04. Assigned a static IP to it.
2. **Setup Script (`server_setup.sh`):** Created a one-time bash script to install Python 3.12, Nginx, MySQL, and create the required systemd services for Gunicorn.
3. **Deployment Pipeline (`deploy_vps.ps1` & `remote_deploy.sh`):** Created a seamless PowerShell script that archives the local codebase, securely transfers it to the server using SCP, and triggers a remote bash script to apply migrations, collect static files, and restart the live app automatically.
4. **Environment Variables:** Rebuilt the `.env` handling. Elastic Beanstalk relied on OS-level variables. We retrofitted `settings.py` to securely read a `.env` file instead, allowing systemd/Gunicorn to easily boot up.

### Challenges & Fixes During Migration:

**1. PyMySQL Missing on Ubuntu Native Python**

- **Symptom:** `import PyMySQL` failed inside settings, causing server 500 errors.
- **Fix:** Switched database driver directly back to `mysqlclient` via standard Django `django.db.backends.mysql` since we had full root access to install native C bindings (`libmysqlclient-dev`).

**2. Duplicate Google OAuth Social App**

- **Symptom:** The `/owner/login/` page threw a 500 server error because the database had duplicate `SocialApp` configurations for Google.
- **Fix:** Created a SQL script (`fix_duplicate_oauth.sql`) to purge duplicates and properly seed the exact Client ID and Secret for the domain.

**3. Missing Styles (CSS 404s)**

- **Symptom:** The website operated but looked un-styled.
- **Fix:** Found that Nginx was initially configured with `root /var/www/...` in the `/static/` location block, which mapped to `/static/staticfiles`. Modified Nginx to explicitly use `alias /var/www/bot_management_system/staticfiles/`. This instantly restored stylesheets.

**4. Add Bot Button Silently Failing (Emoji Support)**

- **Symptom:** Clicking "Add Bot" completely failed without any on-screen error.
- **Fix:** Traced the issue through Gunicorn API logs and found that MySQL returned the error `Incorrect string value: '\xF0\x9F\x91\x8B...'` due to a waving hand emoji (`👋`) in the default welcome message. The new MySQL database was created with the default `utf8` character set. Converted the entire database and all tables to `utf8mb4` with the `utf8mb4_unicode_ci` collation to natively support 4-byte characters like emojis.
