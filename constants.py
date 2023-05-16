DB_SHCEMA = """
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
  PRIMARY KEY (`project_id`,`name`),
  KEY `ix_runs_user_id` (`user_id`),
  KEY `runs_created_at_idx` (`project_id`,`created_at`),
  KEY `ix_runs_state` (`state`,`project_id`,`name`),
  KEY `runs_sweep_idx` (`project_id`,`sweep_name`),
  KEY `runs_global_created_at_idx` (`created_at`),
  KEY `runs_global_deleted_at_idx` (`deleted_at`)
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
  KEY `alerts_ibfk_1` (`entity_id`),
  KEY `alerts_ibfk_2` (`project_id`),
  KEY `alerts_ibfk_3` (`view_id`),
  CONSTRAINT `alerts_ibfk_1` FOREIGN KEY (`entity_id`) REFERENCES `entities` (`id`),
  CONSTRAINT `alerts_ibfk_2` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`),
  CONSTRAINT `alerts_ibfk_3` FOREIGN KEY (`view_id`) REFERENCES `views` (`id`)
)
"""