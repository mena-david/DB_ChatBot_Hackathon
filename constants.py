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
    "In order to determine if a users belongs to an organizations you need to look at the organization_members table.",
    "The customer_subscription_id for an organization is the customer_subscription_id for the user whose value on is_billing_user is true under organization_members table",
    "To connect an organization to stripe_customer_id, we get the stripe_cutomer_id for the billing user for that organization on the organization_members_table. ",
    "Organizations can have multiple subscriptions. ",
    "To determine whether a user is a 'paying user', the is_paid column on the entities table must be of value 1 and the user must not belong to an organization. The organization_id column does not indicate if the user is part of the organization refer to organization_members",
    "To check if a user is part of an organization we need to check the organization_members table. "
    "Only subscription of type 'stripe' has a stripe_subscription_id. Enterprise does not have a stripe_subscription_id. ",
    "stripe_subscription_ids are ONLY found on the organization_subscriptions table. ",
    "Type of subscription is found on the organization_subscription table under the subscription_type column. The types are 'enterprise', 'stripe', 'manual_trial', 'user_led_trial', 'academic_trial', 'academic', 'local'. ",
    "admin users have a value of 1 on the admin column on the users table. ",
    "Enterprise users are those part of an organization who has a subscription with subscription_type = 'enterprise' and subscription_status = enabled. ",
    "The status of an organization, enabled or disabled, is determined by the status of the primary subscription associated with that organization. Only check status whenever asked.",
    "to determine if a subscription is a primary subscription, we need to check the plan_id on the organization_subscription table to the corresponing entry on plans table on the plan_type column. "
    "the plan_type on the plans table indicates whether is a 'primary', 'storage', 'reference', ",
    "To connect runs to an organization, from the runs table we match the project_id column to the id column on the projects table where we match the entity_id column on projects tabe to the id column on entities table which has an organization_id column. ",
    "runs.project_id only corresponds with projects.id. projects.entity_id corresponds with entity.id. entity.organization_id corresponds with organization.id and organization_subscription.organization_id",
    "When asked 'what is the user' or 'which users' make sure to include the name of the user as part of the answer. "
]




OLD_DB_SCHEMA = """
TABLE `organizations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  `org_type` varchar(64) NOT NULL DEFAULT 'ORGANIZATION',
  `flags` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
)

TABLE `plans` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `stripe_plan_id` varchar(64) DEFAULT NULL,
  `max_seats` int(11) NOT NULL,
  `default_privileges` json NOT NULL,
  `plan_type` varchar(64) NOT NULL,
  `plan_visibility` varchar(64) NOT NULL DEFAULT 'public',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  `display_name` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_plan_name` (`name`)
)

TABLE `organization_subscriptions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `organization_id` int(11) NOT NULL,
  `plan_id` int(11) NOT NULL,
  `privileges` json NOT NULL,
  `stripe_subscription_id` varchar(64) DEFAULT NULL,
  `seats` int(11) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  `subscription_type` varchar(64) NOT NULL DEFAULT 'stripe',
  `expires_at` datetime DEFAULT NULL,
  `status` varchar(16) NOT NULL DEFAULT 'enabled',
  `is_automatic_upgrade` tinyint(1) DEFAULT '0',
  `threshold_crossed_at` datetime DEFAULT NULL,
  `upgraded_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `organization_subscriptions_ibfk_1` (`organization_id`),
  KEY `organization_subscriptions_ibfk_2` (`plan_id`),
  CONSTRAINT `organization_subscriptions_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`),
  CONSTRAINT `organization_subscriptions_ibfk_2` FOREIGN KEY (`plan_id`) REFERENCES `plans` (`id`)
)

TABLE `organization_members` (
  `organization_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `role` varchar(64) DEFAULT 'member',
  `is_billing_user` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`organization_id`,`user_id`),
  KEY `organization_members_ibfk_2` (`user_id`),
  CONSTRAINT `organization_members_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`),
  CONSTRAINT `organization_members_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)

TABLE `users` (
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(64) DEFAULT NULL,
  `auth_id` varchar(400) DEFAULT NULL,
  `name` varchar(64) DEFAULT NULL,
  `username` varchar(64) DEFAULT NULL,
  `photo_url` mediumtext,
  `admin` tinyint(1) DEFAULT NULL,
  `default_entity_id` int(11) DEFAULT NULL,
  `account_type` varchar(64) DEFAULT NULL,
  `logged_in_at` datetime DEFAULT NULL,
  `analytics` mediumtext,
  `user_info` json DEFAULT NULL,
  `private` tinyint(1) NOT NULL DEFAULT '0',
  `user_info_text` longtext,
  `stripe_customer_id` varchar(64) DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `onboarding_steps` json DEFAULT NULL,
  `hide_teams_from_public` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_auth_id` (`auth_id`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `ix_users_username` (`username`),
  KEY `default_entity_id` (`default_entity_id`),
  KEY `users_created_at_idx` (`created_at`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`default_entity_id`) REFERENCES `entities` (`id`)
)

TABLE `runs` (
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL,
  `project_id` int(11) NOT NULL,
  `name` varchar(128) NOT NULL,
  `job_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `sweep_name` varchar(64) DEFAULT NULL,
  `config` json DEFAULT NULL,
  `summary_metrics` json DEFAULT NULL,
  `system_metrics` json DEFAULT NULL,
  `state` varchar(64) DEFAULT NULL,
  `commit` varchar(64) DEFAULT NULL,
  `host` varchar(64) DEFAULT NULL,
  `exitcode` bigint(20) DEFAULT NULL,
  `description` mediumtext,
  `heartbeat_at` datetime DEFAULT NULL,
  `group_name` varchar(128) DEFAULT NULL,
  `subgroup_name` varchar(128) DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `history_count` bigint(20) DEFAULT '0',
  `event_count` bigint(20) DEFAULT '0',
  `log_count` bigint(20) DEFAULT '0',
  `stopped` tinyint(1) DEFAULT '0',
  `keys_info` json DEFAULT NULL,
  `agent_id` varchar(128) DEFAULT NULL,
  `tags_json` json DEFAULT NULL,
  `display_name` mediumtext,
  `notes` mediumtext,
  `default_color_idx` int(11) DEFAULT NULL,
  PRIMARY KEY (`project_id`,`name`)
)

TABLE `alert_subscriptions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `alert_id` int(11) NOT NULL,
  `integration_id` int(11) DEFAULT NULL,
  `type` varchar(64) NOT NULL,
  `config` json NOT NULL,
  `created_at` datetime NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `alert_subscriptions_ibfk_1` (`alert_id`),
  KEY `alert_subscriptions_ibfk_2` (`integration_id`),
  KEY `alert_subscriptions_ibfk_3` (`user_id`),
  CONSTRAINT `alert_subscriptions_ibfk_1` FOREIGN KEY (`alert_id`) REFERENCES `alerts` (`id`),
  CONSTRAINT `alert_subscriptions_ibfk_2` FOREIGN KEY (`integration_id`) REFERENCES `integrations` (`id`),
  CONSTRAINT `alert_subscriptions_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)

TABLE `alerts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entity_id` int(11) DEFAULT NULL,
  `project_id` int(11) DEFAULT NULL,
  `type` varchar(64) NOT NULL,
  `config` json NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `view_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `alerts_ibfk_1` FOREIGN KEY (`entity_id`) REFERENCES `entities` (`id`),
  CONSTRAINT `alerts_ibfk_2` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`)
)

TABLE `entities` (
  `created_at` datetime NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `default_access` varchar(64) NOT NULL DEFAULT 'USER_READ',
  `is_team` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `is_paid` tinyint(1) NOT NULL DEFAULT '0',
  `rate_limits` json DEFAULT NULL,
  `settings` json DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `entities_ibfk_2` FOREIGN KEY (`claiming_entity_id`) REFERENCES `entities` (`id`),
  CONSTRAINT `entities_ibfk_3` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`)
)

TABLE `projects` (
  `created_at` datetime NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entity_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `name` varchar(128) DEFAULT NULL,
  `access` varchar(64) DEFAULT NULL,
  `views` json DEFAULT NULL,
  `description` text,
  `group_path` varchar(256) DEFAULT NULL,
  `featured` int(11) DEFAULT NULL,
  `storage_key` varchar(128) NOT NULL,
  `is_published` tinyint(1) NOT NULL DEFAULT '0',
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `projects_ibfk_1` FOREIGN KEY (`entity_id`) REFERENCES `entities` (`id`),
  CONSTRAINT `projects_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `projects_ibfk_3` FOREIGN KEY (`benchmark_id`) REFERENCES `projects` (`id`)
)
"""