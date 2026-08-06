SELECT *
FROM telemetri_data_warehouse_test.dahua_dsm_alarms_test
WHERE
    DOOR_NUMBER LIKE 'A%'
    AND toDate(ALARM_DATE) BETWEEN '2026-07-24' AND '2026-07-27'
ORDER BY
    ALARM_DATE,
    DOOR_NUMBER;