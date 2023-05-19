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

TABLE `sweeps` (
  `created_at` datetime,
  `updated_at` datetime,
  `project_id` int,
  `name` string,
  `method` string,
  `state` string,
  `description` mediumtext,
  `user_id` int,
  `config` json,
  `heartbeat_at` datetime,
  `early_stop_job_running` tinyint(1),
)

TABLE `teams` (
  `user_id` int,
  `entity_id` int,
  `type` string,
  `config` json ,
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
    "In order to determine if a users belongs to an organizations you need to look at the organization_members table.",
    "The customer_subscription_id for an organization is the customer_subscription_id for the user whose value on is_billing_user is true under organization_members table",
    "To connect an organization to stripe_customer_id, we get the stripe_cutomer_id for the billing user for that organization on the organization_members_table. ",
    "Organizations can have multiple subscriptions. ",
    "stripe_subscription_id for an organization is found on the organization_subscriptions table",
    "To determine whether a user is a 'paying user', the is_paid column on the entities table must be of value 1 and the user must not belong to an organization. The organization_id column does not indicate if the user is part of the organization refer to organization_members",
    "To check if a user is part of an organization we need to check the organization_members table. "
    "Only subscription of type 'stripe' has a stripe_subscription_id. ",
    "stripe_subscription_ids are ONLY found on the organization_subscriptions table. ",
    "Type of subscription is found on the organization_subscription table under the subscription_type column. The types are 'enterprise', 'stripe', 'manual_trial', 'user_led_trial', 'academic_trial', 'academic', 'local'. ",
    "admin users have a value of 1 on the admin column on the users table. ",
    "then entities tables holds users and teams. If a team is part of an organization, the organization_id will included the organization_id that team is a part of"
    "team name is found on the entities table under the name column for all entities where is_team = 1. teams.name Does NOT exist"
    "the teams table groups users by entity_id. The name of the team is the value on the name column on the entities table for that entity_id. ",
    "a starter customer is an organization who has a subscription with a plan_id of 15, 16, 17, 18, 19, or 20 which corresponds to plan.name of 'starter_tier_1_monthly', 'starter_tier_1_yearly', 'starter_tier_2_monthly', 'starter_tier_2_yearly', 'starter_tier_3_monthly' or 'starter_tier_3_yearly'"
    "Enterprise users are those part of an organization who has a subscription with subscription_type = 'enterprise' and subscription_status = enabled. ",
    "The status of an organization, enabled or disabled, is determined by the status of the primary subscription associated with that organization. Only check status when asked.",
    "to determine if a subscription is a primary subscription, we need to check the plan_id on the organization_subscription table to the corresponing entry on plans table on the plan_type column. "
    "the plan_type on the plans table indicates whether is a 'primary', 'storage', 'reference', ",
    "To connect runs to an organization, from the runs table we match the project_id column to the id column on the projects table where we match the entity_id column on projects tabe to the id column on entities table which has an organization_id column. ",
    "runs.project_id only corresponds with projects.id. projects.entity_id corresponds with entity.id. entity.organization_id corresponds with organization.id and organization_subscription.organization_id",
    "To connect sweeps to an organization, from the sweeps table we match the project_id column to the id column on the projects table where we match the entity_id column on projects tabe to the id column on entities table which has an organization_id column. ",
    "sweeps.project_id only corresponds with projects.id. projects.entity_id corresponds with entity.id. entity.organization_id corresponds with organization.id and organization_subscription.organization_id",
    "When asked 'what is the user' or 'which users' make sure to include the name of the user as part of the answer. "
]
