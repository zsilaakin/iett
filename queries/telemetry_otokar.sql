SELECT
    DOOR_NUMBER,
    TS,
    DRIVER_NAME
FROM telemetri_data_warehouse_test.telemetri_fact_otokar_test
WHERE
    DRIVER_NAME IS NOT NULL
ORDER BY
    TS,
    DOOR_NUMBER