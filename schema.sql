CREATE TABLE IF NOT EXISTS companies
(
  id        INT AUTO_INCREMENT PRIMARY KEY,
  name      VARCHAR(255) UNIQUE,
  full_name VARCHAR(255) DEFAULT ''
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  DEFAULT CHARACTER SET = utf8
  DEFAULT COLLATE utf8_unicode_ci;
CREATE TABLE IF NOT EXISTS prices
(
  id              INT AUTO_INCREMENT PRIMARY KEY,
  company_id      INT UNSIGNED,
  current         DECIMAL(8, 2),
  high            DECIMAL(8, 2),
  low             DECIMAL(8, 2),
  volume          BIGINT,
  volume_previous BIGINT NULL DEFAULT NULL,
  time            TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  DEFAULT CHARACTER SET = utf8
  DEFAULT COLLATE utf8_unicode_ci;
CREATE TABLE IF NOT EXISTS news
(
  id         INT AUTO_INCREMENT PRIMARY KEY,
  company_id INT UNSIGNED,
  link       VARCHAR(255),
  prediction DECIMAL(8, 4),
  actual     DECIMAL(8, 4),
  time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  DEFAULT CHARACTER SET = utf8
  DEFAULT COLLATE utf8_unicode_ci;


