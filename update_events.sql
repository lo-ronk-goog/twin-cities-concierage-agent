-- BigQuery SQL script to shift all event dates so that they fall inside the current week
-- Dynamically targets the Sunday ending the current week (Monday=day 1 ... Sunday=day 7).
-- Stores dates in standard ISO YYYY-MM-DD format.

DECLARE target_sunday DATE;
DECLARE max_date DATE;

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
