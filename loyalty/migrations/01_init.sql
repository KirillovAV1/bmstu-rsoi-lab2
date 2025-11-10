CREATE TABLE loyalty
(
    id                SERIAL PRIMARY KEY,
    username          VARCHAR(80) NOT NULL UNIQUE,
    reservation_count INT         NOT NULL DEFAULT 0,
    status            VARCHAR(80) NOT NULL DEFAULT 'BRONZE'
        CHECK (status IN ('BRONZE', 'SILVER', 'GOLD')),
    discount          INT         NOT NULL
);

INSERT INTO loyalty (id, username, reservation_count, status, discount) VALUES
(1,'Test Max',25,'GOLD',10)
ON CONFLICT (id) DO NOTHING;