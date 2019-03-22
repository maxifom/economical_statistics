SET NAMES utf8;
SET collation_connection = utf8_general_ci;
create table if not exists economics.companies
(
  id         int auto_increment
    primary key,
  name       varchar(255)            null,
  full_name  varchar(255) default '' null,
  parse_name varchar(255)            null,
  ticker     varchar(255)            null,
  url        varchar(255)            null,
  constraint name
    unique (name)
) collate = utf8_unicode_ci;
create table if not exists economics.news
(
  id                    int auto_increment
    primary key,
  company_id            int unsigned   null,
  link                  varchar(255)   null,
  body                  text           null,
  prediction            decimal(15, 8) null,
  actual                decimal(15, 8) null,
  time                  timestamp               default CURRENT_TIMESTAMP not null,
  sent_score            decimal(15, 8) null,
  word_count            int            null,
  log_return            decimal(15, 8) null,
  trading_volume        decimal(15, 8) null,
  overnight_variation   decimal(15, 8) null,
  trading_day_variation decimal(15, 8) null,
  closing_price         decimal(15, 8) null,
  seen                  tinyint(1)     not null default '0',
  parsed                tinyint(1)     not null default '0'
) collate = utf8_unicode_ci;
create table if not exists economics.prices
(
  id              int auto_increment
    primary key,
  company_id      int unsigned                        null,
  current         decimal(8, 2)                       null,
  high            decimal(8, 2)                       null,
  low             decimal(8, 2)                       null,
  volume          bigint                              null,
  volume_previous bigint                              null,
  time            timestamp default CURRENT_TIMESTAMP not null
) collate = utf8_unicode_ci;
CREATE TABLE IF NOT EXISTS economics.words (
  id int(11) NOT NULL AUTO_INCREMENT,
  word varchar(255) NOT NULL,
  is_positive tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (id),
  UNIQUE KEY word (word)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE = utf8_unicode_ci;
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (1, 'Safmar Fin', 'Safmar Finansovye Investitsii PAO', 'Сафмар, Safmar', 'SFIN',
        'https://ru.investing.com/equities/yevroplan-pao');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (2, 'X5 Retail Group', 'X5 Retail Group NV', 'X5', 'FIVE',
        'https://ru.investing.com/equities/x5-retail-grp?cid=1061926');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (3, 'АК АЛРОСА', 'ОАО АК АЛРОСА', 'Алроса', 'ALRS', 'https://ru.investing.com/equities/alrosa-ao');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (4, 'Аэрофлот', 'ОАО Аэрофлот', 'Аэрофлот', 'AFLT', 'https://ru.investing.com/equities/aeroflot');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (5, 'Банк ВТБ', 'Банк ВТБ (ОАО)', 'ВТБ, Втб', 'VTBR', 'https://ru.investing.com/equities/vtb_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (6, 'Газпром', 'Газпром ПАО', 'Газпром', 'GAZP', 'https://ru.investing.com/equities/gazprom_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (7, 'Группа Компаний ПИК', 'ОАО Группа Компаний ПИК', 'ПИК', 'PIKK',
        'https://ru.investing.com/equities/pik_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (8, 'Детский мир', 'Детский мир ПАО', 'Детский мир', 'DSKY',
        'https://ru.investing.com/equities/detskiy-mir-pao');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (9, 'Интер РАО ЕЭС ОАО', 'Интер РАО ЕЭС ОАО', 'Интер', 'IRAO',
        'https://ru.investing.com/equities/inter-rao-ees_mm');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (10, 'ЛУКОЙЛ', 'ОАО ЛУКОЙЛ', 'Лукойл, ЛУКОЙЛ', 'LKOH', 'https://ru.investing.com/equities/lukoil_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (11, 'М.видео', 'ОАО Компания «М.видео»', 'М.Видео, МВидео, М. Видео, М.видео', 'MVID',
        'https://ru.investing.com/equities/mvideo_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (12, 'Магнит', 'ОАО Магнит', 'Магнит', 'MGNT', 'https://ru.investing.com/equities/magnit_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (13, 'МегаФон ОАО', 'МегаФон ОАО', 'Мегафон, МегаФон', 'MFON', 'https://ru.investing.com/equities/megafon-oao');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (14, 'Мечел', 'Мечел', 'Мечел', 'MTLR', 'https://ru.investing.com/equities/sg-mechel_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (15, 'МКБ', 'Московский кредитный банк', 'МКБ, Московский кредитный банк', 'CBOM',
        'https://ru.investing.com/equities/moskovskiy-kreditnyi-bank-oao');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (16, 'ММК ОАО', 'ММК ОАО', 'ММК', 'MAGN', 'https://ru.investing.com/equities/mmk_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (17, 'Московская биржа', 'Московская биржа ОАО', 'Московская биржа', 'MOEX',
        'https://ru.investing.com/equities/moskovskaya-birzha-oao');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (18, 'МТС', 'ОАО Мобильные ТелеСистемы', 'МТС', 'MTSS', 'https://ru.investing.com/equities/mts_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (19, 'НЛМК ОАО', 'Новолипецкий MK', 'НЛМК', 'NLMK', 'https://ru.investing.com/equities/nlmk_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (20, 'НМТП ОАО', 'ОАО Новороссийский МТП', 'НМТП', 'NMTP', 'https://ru.investing.com/equities/nmtp_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (21, 'НОВАТЭК', 'ОАО НОВАТЭК', 'Новатек', 'NVTK', 'https://ru.investing.com/equities/novatek_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (22, 'Норильский никель', 'ОАО ГМК Норильский никель', 'Норильский никель, Норникель', 'GMKN',
        'https://ru.investing.com/equities/gmk-noril-nickel_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (23, 'НПК ОВК', 'НПК Объединенная Вагонная Компания', 'ОВК', 'UWGN',
        'https://ru.investing.com/equities/npk-ovk-pao');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (24, 'Polymetal', 'Полиметалл Интернэшнл плс', 'Полиметал, Polymetal', 'POLY',
        'https://ru.investing.com/equities/polymetal?cid=44465');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (25, 'Полюс', 'Полюс ОАО', 'Полюс', 'PLZL', 'https://ru.investing.com/equities/polyus-zoloto_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (26, 'РОС АГРО ПЛС', 'РОС АГРО ПЛС', 'АГРО ПЛС', 'AGRO', 'https://ru.investing.com/equities/ros-agro-plc');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (27, 'Роснефть', 'Роснефть ПАО', 'Роснефть', 'ROSN', 'https://ru.investing.com/equities/rosneft_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (28, 'Россети', 'Российские сети ОАО', 'Россети', 'RSTI', 'https://ru.investing.com/equities/rosseti-ao');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (29, 'Ростелеком', 'ОАО Ростелеком', 'Ростелеком', 'RTKM', 'https://ru.investing.com/equities/rostelecom');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (30, 'РУСАЛ', 'Юнайтед Компани РУСАЛ Плс', 'Русал', 'RUAL',
        'https://ru.investing.com/equities/united-company-rusal-plc`');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (31, 'РусГидро', 'ОАО РусГидро', 'РусГидро', 'HYDR', 'https://ru.investing.com/equities/gidroogk-011d');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (32, 'РуссНефть', 'РуссНефть ОАО НК', 'РуссНефть', 'RNFT', 'https://ru.investing.com/equities/ruspetro');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (33, 'Сбербанк', 'Сбербанк ПАО', 'Сбербанк', 'SBER', 'https://ru.investing.com/equities/sberbank_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (34, 'Сбербанк (прив.)', 'Сбербанк (прив.)', 'Сбербанк', 'SBERP',
        'https://ru.investing.com/equities/sberbank-p_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (35, 'Северсталь', 'ОАО Северсталь', 'Северсталь', 'CHMF', 'https://ru.investing.com/equities/severstal_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (36, 'Система', 'ОАО АФК Система', 'АФК Система', 'AFKS', 'https://ru.investing.com/equities/afk-sistema_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (37, 'Сургутнефтегаз', 'Surgutneftegaz PAO', 'Сургутнефтегаз', 'SNGS',
        'https://ru.investing.com/equities/surgutneftegas_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (38, 'Сургутнефтегаз (прив.)', 'Сургутнефтегаз (прив.)', 'Сургутнефтегаз', 'SNGSP',
        'https://ru.investing.com/equities/surgutneftegas-p_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (39, 'Татнефть', 'ОАО Татнефть', 'Татнефть', 'TATN', 'https://ru.investing.com/equities/tatneft_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (40, 'Татнефть (прив.)', 'Татнефть (прив.)', 'Татнефть', 'TATNP',
        'https://ru.investing.com/equities/tatneft-p_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (41, 'ТМК ОАО ', 'Трубная металлургическая компания ОАО', 'ТМК', 'TRMK',
        'https://ru.investing.com/equities/tmk');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (42, 'Транснефть (прив.)', 'Транснефть (прив.)', 'Транснефть', 'TRNFP',
        'https://ru.investing.com/equities/transneft-p_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (43, 'ФосАгро', 'ОАО ФосАгро', 'ФосАгро', 'PHOR', 'https://ru.investing.com/equities/phosagro');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (44, 'ФСК ЕЭС ОАО', 'ФСК ЕЭС ОАО', 'ФСК ЕЭС', 'FEES', 'https://ru.investing.com/equities/fsk-ees_rts');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (45, 'Юнипро', 'Юнипро ПАО', 'Юнипро', 'UPRO', 'https://ru.investing.com/equities/e.on-russia');
INSERT IGNORE INTO economics.companies (id, name, full_name, parse_name, ticker, url)
VALUES (46, 'Яндекс', 'Яндекс Н.В.', 'Яндекс', 'YNDX', 'https://ru.investing.com/equities/yandex?cid=102063');
