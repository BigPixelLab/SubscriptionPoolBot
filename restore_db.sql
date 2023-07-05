-- Очищаем базу данных до состояния по умолчанию
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

-- Добавляем таблицы
CREATE TABLE "Client" (
    chat_id bigint not null
        PRIMARY KEY,
    referral_id bigint
        REFERENCES "Client" (chat_id),
    season_points bigint not null
        DEFAULT 0,
    terms_message_id bigint,
    created_at timestamp not null
);

CREATE INDEX Client_pk ON "Client" (chat_id);
CREATE INDEX Client_referral_id ON "Client" (referral_id);


CREATE TABLE "Employee" (
    chat_id bigint not null
        PRIMARY KEY
        REFERENCES "Client" (chat_id)
);

CREATE INDEX Employee_pk ON "Employee" (chat_id);


CREATE TABLE "CouponType" (
    id varchar not null
        PRIMARY KEY,
    subscription_group_id varchar not null,  -- Fk added later
    discount numeric(1000, 2) not null
        CHECK ( discount >= 0 and discount <= 100 ),
    max_usages bigint,
    lifespan interval,
    allows_gifts bool not null
);

CREATE INDEX CouponType_pk ON "CouponType" (id);
CREATE INDEX CouponType_subscription_group_id ON "CouponType" (subscription_group_id);


CREATE TABLE "Coupon" (
    code varchar not null
        PRIMARY KEY,
    type_id varchar not null
        REFERENCES "CouponType" (id),
    sets_referral_id bigint
        REFERENCES "Client" (chat_id),
    created_at timestamp not null
);

CREATE INDEX Coupon_pk ON "Coupon" (code);
CREATE INDEX Coupon_type_id ON "Coupon" (type_id);
CREATE INDEX Coupon_sets_referral_id ON "Coupon" (sets_referral_id);


CREATE TABLE "Subscription" (
    id varchar not null
        PRIMARY KEY,
    gift_coupon_type_id varchar
        REFERENCES "CouponType" (id),
    service_id varchar not null,
    short_title varchar not null,
    title varchar not null,
    duration interval
        CHECK ( duration IS NULL
        	OR duration > interval '0' ),
    price numeric(1000, 2) not null
        CHECK ( price >= 0 ),
    category varchar not null
);

CREATE INDEX Subscription_pk ON "Subscription" (id);
CREATE INDEX Subscription_gift_coupon_type_id ON "Subscription" (gift_coupon_type_id);


CREATE TABLE "SubscriptionGroup" (
    id varchar not null
        PRIMARY KEY,
    parent_id varchar
        REFERENCES "SubscriptionGroup" (id),
    subscription_id varchar
        REFERENCES "Subscription" (id)
);

-- Adding constraint that cannot been added due to circular references
ALTER TABLE "CouponType" ADD CONSTRAINT fk_SubscriptionGroup
    FOREIGN KEY (subscription_group_id) REFERENCES "SubscriptionGroup" (id);

CREATE INDEX SubscriptionGroup_pk ON "SubscriptionGroup" (id);
CREATE INDEX SubscriptionGroup_parent_id ON "SubscriptionGroup" (parent_id);
CREATE INDEX SubscriptionGroup_subscription_id ON "SubscriptionGroup" (subscription_id);


CREATE TABLE "Order" (
    id serial not null
        PRIMARY KEY,
    client_id bigint not null
        REFERENCES "Client" (chat_id),
    subscription_id varchar not null
        REFERENCES "Subscription" (id),
    coupon_id varchar
        REFERENCES "Coupon" (code),
    processing_employee_id bigint
        REFERENCES "Employee" (chat_id),
    paid_amount numeric(1000, 2) not null
        CHECK ( paid_amount >= 0 ),
    created_at timestamp not null,
    closed_at timestamp,
    notified_renew bool not null
);

CREATE INDEX Order_pk ON "Order" (id);
CREATE INDEX Order_client_id ON "Order" (client_id);
CREATE INDEX Order_subscription_id ON "Order" (subscription_id);
CREATE INDEX Order_coupon_id ON "Order" (coupon_id);
CREATE INDEX Order_processing_employee_id ON "Order" (processing_employee_id);


CREATE TABLE "Bill" (
    client_id bigint not null
        PRIMARY KEY,
    subscription_id varchar not null
        REFERENCES "Subscription" (id),
    coupon_id varchar
        REFERENCES "Coupon" (code),
    qiwi_id varchar not null,
    message_id bigint not null,
    expires_at timestamp not null
);

CREATE INDEX Bill_pk ON "Bill" (client_id);
CREATE INDEX Bill_subscription_id ON "Bill" (subscription_id);
CREATE INDEX Bill_coupon_id ON "Bill" (coupon_id);


CREATE TABLE "ResourceCache" (
    path varchar not null,
    bot_id bigint not null,
    file_id varchar not null,

    PRIMARY KEY (path, bot_id)
);

CREATE INDEX ResourceCache_pk ON "ResourceCache" (bot_id, path);


CREATE TABLE "Season" (
    id int not null
        PRIMARY KEY,
    description text not null
);

CREATE INDEX Season_pk ON "Season" (id);


CREATE TABLE "SeasonPrize" (
    id int not null
        PRIMARY KEY,
    coupon_type_id varchar not null
        REFERENCES "CouponType" (id),
    banner varchar not null,
    title varchar not null,
    cost bigint not null
        CHECK ( cost >= 0 )
);

CREATE INDEX SeasonPrize_pk ON "SeasonPrize" (id);
CREATE INDEX SeasonPrize_coupon_type_id ON "SeasonPrize" (coupon_type_id);


CREATE TABLE "Lottery" (
    id varchar not null
        PRIMARY KEY,
    banner varchar not null,
    title varchar not null,
    description text not null
);

CREATE INDEX Lottery_pk ON "Lottery" (id);


CREATE TABLE "LotteryPrize" (
    id serial not null
        PRIMARY KEY,
    lottery_id varchar not null
        REFERENCES "Lottery" (id),
    coupon_type_id varchar not null
        REFERENCES "CouponType" (id),
    weight int not null,
    count int,

    banner varchar not null,
    title varchar not null,
    description text not null,

    -- Only one of "weight" and "count" must be filled
    CONSTRAINT ether_weight_or_cost_specified
        CHECK ( (weight is null) != (count is null) )
);

CREATE INDEX LotteryPrize_pk ON "LotteryPrize" (id);
CREATE INDEX LotteryPrize_lottery_id ON "LotteryPrize" (lottery_id);
CREATE INDEX LotteryPrize_coupon_type_id ON "LotteryPrize" (coupon_type_id);


CREATE VIEW "SubGroupHierarchyView" AS
WITH RECURSIVE "Group" AS (
    SELECT
        id,
        subscription_id,
        array[]::varchar[] as groups
    FROM "SubscriptionGroup" WHERE parent_id is null

    UNION ALL

    SELECT
        "SubscriptionGroup".id,
        "SubscriptionGroup".subscription_id,
        "Group".groups || "SubscriptionGroup".parent_id
    FROM "SubscriptionGroup", "Group"
    WHERE "SubscriptionGroup".parent_id = "Group".id
)
SELECT
    subscription_id,
    groups || id as groups
FROM "Group"
WHERE subscription_id is not null;


CREATE VIEW "CouponSubscriptionView" AS
SELECT
    "Coupon".code as code,
    "Subscription".id as subscription
FROM "Subscription"
    JOIN "SubGroupHierarchyView" ON "SubGroupHierarchyView".subscription_id = "Subscription".id
    JOIN "CouponType" ON "CouponType".subscription_group_id = any ("SubGroupHierarchyView".groups)
    JOIN "Coupon" ON "Coupon".type_id = "CouponType".id;


-- gift_coupon_type_id должны быть добавлены после того как будут
-- созданы coupon_type.
INSERT INTO "Subscription" (
    id,                 service_id,
    short_title,        title,                  duration,
    price,              category
) VALUES (
    'netflix_4k_1m',    'netflix',
    '4K 30 дней',       'NETFLIX 4K 30 дней',   '30 days'::interval,
    999.00,             '4k'
), (
    'netflix_HD_1m',    'netflix',
    'HD 30 дней',       'NETFLIX HD 30 дней',   '30 days'::interval,
    699.00,             'HD'
), (
    'spotify_ind_1m',   'spotify',
    '1 месяц',          'SPOTIFY 1 месяц',      '30 days'::interval,
    199.00,             ''
), (
    'spotify_ind_3m',   'spotify',
    '3 месяца',         'SPOTIFY 3 месяца',     '90 days'::interval,
    549.00,             ''
), (
    'spotify_ind_6m',   'spotify',
    '6 месяцев',        'SPOTIFY 6 месяцев',    '180 days'::interval,
    999.00,             ''
), (
    'spotify_ind_1y',   'spotify',
    '1 год',            'SPOTIFY 1 год',        '360 days'::interval,
    1499.00,            ''
), (
    'chatgpt_account',  'chatgpt',
    'Аккаунт',          'ChatGPT Аккаунт',     NULL,
    149.00,             'account'
), (
    'chatgpt_plus_1m',  'chatgpt',
    'Plus 1 месяц',     'ChatGPT PLUS+',        '30 days'::interval,
    1999.00,            'plus'
);


INSERT INTO "SubscriptionGroup"
    (id,                parent_id,  subscription_id)
VALUES
    ('all',             null,       null),
    ('spotify',         'all',      null),
    ('spotify_ind_1m',  'spotify',  'spotify_ind_1m'),
    ('spotify_ind_3m',  'spotify',  'spotify_ind_3m'),
    ('spotify_ind_6m',  'spotify',  'spotify_ind_6m'),
    ('spotify_ind_1y',  'spotify',  'spotify_ind_1y'),
    ('netflix',         'all',      null),
    ('netflix_4k_1m',   'netflix',  'netflix_4k_1m'),
    ('netflix_HD_1m',   'netflix',  'netflix_HD_1m'),
    ('chatgpt',         'all',      null),
    ('chatgpt_account', 'chatgpt',  'chatgpt_account'),
    ('chatgpt_plus_1m', 'chatgpt',  'chatgpt_plus_1m');


INSERT INTO "CouponType" (
    id,                     subscription_group_id,  discount,
    max_usages,             lifespan,               allows_gifts
) VALUES (
    'gift_netflix_4k_1m',   'netflix_4k_1m',        100,
    1,                      '30 days'::interval,    false
), (
    'gift_netflix_HD_1m',   'netflix_HD_1m',        100,
    1,                      '30 days'::interval,    false
), (
    'gift_spotify_ind_1m',  'spotify_ind_1m',       100,
    1,                      '30 days'::interval,    false
), (
    'gift_spotify_ind_3m',  'spotify_ind_3m',       100,
    1,                      '90 days'::interval,    false
), (
    'gift_spotify_ind_6m',  'spotify_ind_6m',       100,
    1,                      '180 days'::interval,   false
), (
    'gift_spotify_ind_1y',  'spotify_ind_1y',       100,
    1,                      '360 days'::interval,   false
), (
    'gift_chatgpt_account', 'chatgpt_account',      100,
    1,                      '30 days'::interval,    false
), (
    'gift_chatgpt_plus_1m', 'chatgpt_plus_1m',      100,
    1,                      '30 days'::interval,    false
), (
    'spotify_promo_20',     'spotify',              20,
    null,                   '30 days'::interval,    true
), (
    'spotify_promo_25',     'spotify',              25,
    null,                   '30 days'::interval,    true
), (
    'spotify_promo_30',     'spotify',              30,
    null,                   '30 days'::interval,    true
);


-- Обновляем значения gift_coupon_type_id для подписок
UPDATE "Subscription" SET gift_coupon_type_id = 'gift_netflix_4k_1m' WHERE id = 'netflix_4k_1m';
UPDATE "Subscription" SET gift_coupon_type_id = 'gift_netflix_HD_1m' WHERE id = 'netflix_HD_1m';
UPDATE "Subscription" SET gift_coupon_type_id = 'gift_spotify_ind_1m' WHERE id = 'spotify_ind_1m';
UPDATE "Subscription" SET gift_coupon_type_id = 'gift_spotify_ind_3m' WHERE id = 'spotify_ind_3m';
UPDATE "Subscription" SET gift_coupon_type_id = 'gift_spotify_ind_6m' WHERE id = 'spotify_ind_6m';
UPDATE "Subscription" SET gift_coupon_type_id = 'gift_spotify_ind_1y' WHERE id = 'spotify_ind_1y';
UPDATE "Subscription" SET gift_coupon_type_id = 'gift_chatgpt_account' WHERE id = 'chatgpt_account';
UPDATE "Subscription" SET gift_coupon_type_id = 'gift_chatgpt_plus_1m' WHERE id = 'chatgpt_plus_1m';


INSERT INTO "Client" (chat_id, created_at) VALUES (1099569178, now());
INSERT INTO "Employee" (chat_id) VALUES (1099569178);


INSERT INTO "Lottery"
	(id, banner, title, description)
VALUES (
	'test', 'apps/botpiska/templates/resources/BILL.png', 'WOW!',
	$$
	<section>
		<heading> Yup! </heading>
		<section>
			This is a lottery, totally doesnt look like a scam
		</section>
	</section>
	$$
);


INSERT INTO "LotteryPrize"
	(lottery_id, coupon_type_id, weight, count, banner, title, description)
VALUES
	('test', 'spotify_promo_30', 1, null, 'apps/botpiska/templates/resources/BILL.png', 'Ye', 'Omg');

	
	
	