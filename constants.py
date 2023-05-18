DB_SCHEMA = """
TABLE `organizations` (
  `id` int,
  `name` string,
  `created_at` datetime,
  `updated_at` datetime,
  `org_type` string,
  `flags` json,
)

TABLE `plans` (
  `id` int,
  `name` string,
  `stripe_plan_id` string,
  `max_seats` int,
  `default_privileges` json,
  `plan_type` string,
  `plan_visibility` string,
  `created_at` datetime,
  `updated_at` datetime,
  `display_name` string,
)

TABLE `organization_subscriptions` (
  `id` int,
  `organization_id` int,
  `plan_id` int,
  `privileges` json,
  `stripe_subscription_id` string,
  `seats` int,
  `created_at` datetime,
  `updated_at` datetime,
  `subscription_type` string,
  `expires_at` datetime,
  `status` string,
  `threshold_crossed_at` datetime,
  `upgraded_at` datetime,
)

TABLE `organization_members` (
  `organization_id` int,
  `user_id` int,
  `role` string,
  `is_billing_user` tinyint(1),
  `created_at` datetime,
  `updated_at` datetime.
)

TABLE `users` (
  `created_at` datetime,
  `updated_at` datetime,
  `id` int,
  `email` string,
  `auth_id` string,
  `name` string,
  `username` string,
  `photo_url` mediumtext,
  `admin` tinyint(1),
  `default_entity_id` int,
  `account_type` string,
  `logged_in_at` datetime,
  `analytics` mediumtext,
  `user_info` json,
  `private` tinyint(1),
  `user_info_text` longtext,
  `stripe_customer_id` string,
  `deleted_at` datetime,
  `onboarding_steps` json,
  `hide_teams_from_public` tinyint(1),
)

TABLE `runs` (
  `created_at` datetime,
  `updated_at` datetime,
  `project_id` int,
  `name` string,
  `job_id` int,
  `user_id` int,
  `sweep_name` string,
  `config` json,
  `summary_metrics` json,
  `system_metrics` json,
  `state` string,
  `commit` string,
  `host` string,
  `exitcode` bigint(20),
  `description` mediumtext,
  `heartbeat_at` datetime,
  `group_name` string,
  `subgroup_name` string,
  `deleted_at` datetime,
  `history_count` bigint(20) DEFAULT '0',
  `event_count` bigint(20) DEFAULT '0',
  `log_count` bigint(20) DEFAULT '0',
  `stopped` tinyint(1) DEFAULT '0',
  `keys_info` json,
  `agent_id` string,
  `tags_json` json,
  `display_name` mediumtext,
  `notes` mediumtext,
)

TABLE `alert_subscriptions` (
  `id` int,
  `alert_id` int,
  `integration_id` int,
  `type` string,
  `config` json,
  `created_at` datetime,
  `user_id` int,
)

TABLE `alerts` (
  `id` int,
  `entity_id` int,
  `project_id` int,
  `type` string,
  `config` json,
  `created_at` datetime,
  `updated_at` datetime,
  `view_id` int,
)

TABLE `entities` (
  `created_at` datetime,
  `id` int,
  `name` string,
  `default_access` string,
  `is_team` tinyint(1),
  `organization_id` int,
  `is_paid` tinyint(1)  DEFAULT '0',
  `rate_limits` json,
  `settings` json,
  `deleted_at` datetime,
)

TABLE `projects` (
  `created_at` datetime,
  `id` int,
  `entity_id` int,
  `user_id` int,
  `name` string,
  `access` string,
  `views` json,
  `description` text,
  `group_path` string,
  `featured` int,
  `storage_key` string,
  `is_published` tinyint(1)  DEFAULT '0',
  `deleted_at` datetime,
)
"""

contex_items = [
    "In order to determine what users belong to what organizations you need to look at the organization_members table.",
    "Only users have an associated stripe_customer_id and if they are the billing user for an oganization that stripe_customer_id also belongs to that organization.",
    "To connect an organization to stripe_customer_id, we get the stripe_cutomer_id from the admin user for that organization",
    "Organizations can have multiple subscriptions.",
    "Each subscription of type Stripe has a stripe_subscription_id.",
    "stripe_subscription_ids are ONLY found on the organization_subscriptions table.",
    "Type of subscription is found on the organization_subscription table under the subscription_type column.",
    "admin users have a value of 1 on the admin column on the users table.",
    "Enterprise users are those part of an organization who has a subscription with plan.name Enterprise.",
    "runs table DOES NOT have ID column, just a name column",
    "The status of an organization, active or disabled, is determined by the status of the primary subscription associated with that organization.",
    "To connect runs to an organization, from the runs table we match the project_id column to the id column on the projects table where we match the entity_id column to the id column on entities table which has an organization_id column",
    "When asked 'what is the user' make sure to include the name of the user as part of the answer "
]