-- ==============================================================================
-- BigQuery SQL script to update event dates for October 2026
-- Dataset: lpr-gemini-enterprise-1.msp_coffee_and_music.events
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- OPTION 1: Shift events to current week (Thursday Oct 01 - Sunday Oct 04, 2026)
-- ------------------------------------------------------------------------------
DECLARE target_sunday DATE;
DECLARE max_date DATE;

-- Target Sunday: Oct 4, 2026 (or dynamically the Sunday ending the current week)
SET target_sunday = DATE_ADD(DATE_TRUNC(CURRENT_DATE(), WEEK(MONDAY)), INTERVAL 6 DAY);

SET max_date = (
    SELECT MAX(
        CASE
            WHEN REGEXP_CONTAINS(event_date, r'^\d{4}-\d{2}-\d{2}$')
            THEN PARSE_DATE('%Y-%m-%d', event_date)
            ELSE PARSE_DATE('%Y-%B-%d', event_date)
        END
    )
    FROM `lpr-gemini-enterprise-1.msp_coffee_and_music.events`
);

UPDATE `lpr-gemini-enterprise-1.msp_coffee_and_music.events`
SET event_date = FORMAT_DATE(
    '%Y-%m-%d',
    DATE_ADD(
        CASE
            WHEN REGEXP_CONTAINS(event_date, r'^\d{4}-\d{2}-\d{2}$')
            THEN PARSE_DATE('%Y-%m-%d', event_date)
            ELSE PARSE_DATE('%Y-%B-%d', event_date)
        END,
        INTERVAL DATE_DIFF(target_sunday, max_date, DAY) DAY
    )
)
WHERE TRUE;

-- ------------------------------------------------------------------------------
-- OPTION 2: Replicate events across all 4 weekends of October 2026
-- (Ensures live demo queries work for ANY weekend in October: Oct 1-4, 8-11, 15-18, 22-25)
-- ------------------------------------------------------------------------------
/*
CREATE OR REPLACE TABLE `lpr-gemini-enterprise-1.msp_coffee_and_music.events` AS
WITH base_events AS (
    SELECT
        event_id,
        venue_id,
        artist,
        genre,
        start_time,
        CASE
            WHEN REGEXP_CONTAINS(event_date, r'^\d{4}-\d{2}-\d{2}$')
            THEN PARSE_DATE('%Y-%m-%d', event_date)
            ELSE PARSE_DATE('%Y-%B-%d', event_date)
        END AS parsed_date
    FROM `lpr-gemini-enterprise-1.msp_coffee_and_music.events`
),
normalized_week1 AS (
    SELECT
        event_id,
        venue_id,
        artist,
        genre,
        start_time,
        DATE_ADD(
            parsed_date,
            INTERVAL DATE_DIFF(DATE('2026-10-04'), (SELECT MAX(parsed_date) FROM base_events), DAY) DAY
        ) AS event_date_week1
    FROM base_events
),
all_weeks AS (
    SELECT
        event_id, venue_id, artist, genre, start_time,
        FORMAT_DATE('%Y-%m-%d', event_date_week1) AS event_date
    FROM normalized_week1
    UNION ALL
    SELECT
        CONCAT(event_id, '-W2'), venue_id, artist, genre, start_time,
        FORMAT_DATE('%Y-%m-%d', DATE_ADD(event_date_week1, INTERVAL 7 DAY)) AS event_date
    FROM normalized_week1
    UNION ALL
    SELECT
        CONCAT(event_id, '-W3'), venue_id, artist, genre, start_time,
        FORMAT_DATE('%Y-%m-%d', DATE_ADD(event_date_week1, INTERVAL 14 DAY)) AS event_date
    FROM normalized_week1
    UNION ALL
    SELECT
        CONCAT(event_id, '-W4'), venue_id, artist, genre, start_time,
        FORMAT_DATE('%Y-%m-%d', DATE_ADD(event_date_week1, INTERVAL 21 DAY)) AS event_date
    FROM normalized_week1
)
SELECT * FROM all_weeks;
*/
