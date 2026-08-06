SELECT
    ID,
    DOOR_NUMBER,
    EVENT_START_TIME
FROM telemetri_data_warehouse_test.kts_accidents_test
WHERE
    DOOR_NUMBER LIKE 'O%'
ORDER BY
    EVENT_START_TIME,
    DOOR_NUMBER