-- BigQuery SQL script to shift all event dates so that they fall inside the current week
-- Current Week: Monday, August 10, 2026 to Sunday, August 16, 2026
-- This script shifts all event dates by the difference between the dataset's maximum date and Sunday, August 16, 2026.

DECLARE max_date DATE;
SET max_date = (SELECT MAX(event_date) FROM `lpr-gemini-enterprise-1.msp_coffee_and_music.events`);

UPDATE `lpr-gemini-enterprise-1.msp_coffee_and_music.events`
SET event_date = DATE_ADD(event_date, INTERVAL DATE_DIFF(DATE('2026-08-16'), max_date, DAY) DAY)
WHERE TRUE;
