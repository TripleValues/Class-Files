-- 출발지연횟수 sql문

CREATE TABLE db_air.`출발지연회수` AS
SELECT  
    air.`도시`,
    COUNT(CASE WHEN t.`년도` = 1987 THEN 1 END) AS cnt_1987,
    ROUND(AVG(CASE WHEN t.`년도` = 1987 
            THEN CAST(t.`출발지연시간` AS SIGNED) END),1) AS delay_1987,
    COUNT(CASE WHEN t.`년도` = 1988 THEN 1 END) AS cnt_1988,
    ROUND(AVG(CASE WHEN t.`년도` = 1988 
            THEN CAST(t.`출발지연시간` AS SIGNED) END),1) AS delay_1988,
    COUNT(CASE WHEN t.`년도` = 1989 THEN 1 END) AS cnt_1989,
    ROUND(AVG(CASE WHEN t.`년도` = 1989 
            THEN CAST(t.`출발지연시간` AS SIGNED) END),1) AS delay_1989
FROM db_air.`비행` AS t
INNER JOIN db_air.`항공사` AS air
    ON t.`출발공항코드` = air.`항공사코드`
WHERE air.`도시` IN ('Newark','Atlanta','Chicago','Dallas-Fort Worth','Denver','Houston','Los Angeles','New York','Phoenix','San Francisco','St Louis')
AND t.`출발지연시간` <> 'NA'
GROUP BY air.`도시`;

-- 도착지연횟수 sql문

CREATE TABLE db_air.`도착지연회수` AS
SELECT  
    air.`도시`,
    COUNT(CASE WHEN t.`년도` = 1987 THEN 1 END) AS cnt_1987,
    ROUND(AVG(CASE WHEN t.`년도` = 1987 
            THEN CAST(t.`도착지연시간` AS SIGNED) END),1) AS delay_1987,
    COUNT(CASE WHEN t.`년도` = 1988 THEN 1 END) AS cnt_1988,
    ROUND(AVG(CASE WHEN t.`년도` = 1988 
            THEN CAST(t.`도착지연시간` AS SIGNED) END),1) AS delay_1988,
    COUNT(CASE WHEN t.`년도` = 1989 THEN 1 END) AS cnt_1989,
    ROUND(AVG(CASE WHEN t.`년도` = 1989 
            THEN CAST(t.`도착지연시간` AS SIGNED) END),1) AS delay_1989
FROM db_air.`비행` AS t
INNER JOIN db_air.`항공사` AS air
    ON t.`도착지공항코드` = air.`항공사코드`
WHERE air.`도시` IN ('Newark','Atlanta','Chicago','Dallas-Fort Worth','Denver','Houston','Los Angeles','New York','Phoenix','San Francisco','St Louis')
AND t.`도착지연시간` <> 'NA'
GROUP BY air.`도시`;

-- 월별 인기 노선 sql문

CREATE TABLE db_air.`인기항공노선` AS
SELECT t.`년도`, t.`월`, t.`노선`, t.cnt
FROM (
    SELECT 
        a.`년도`,
        a.`월`,
        CONCAT(air.`도시`, '→', air2.`도시`) AS 노선,
        COUNT(*) AS cnt,
        ROW_NUMBER() OVER (
            PARTITION BY a.`년도`, a.`월`
            ORDER BY COUNT(*) DESC
        ) AS 순위
    FROM `비행` AS a
    INNER JOIN db_air.`항공사` AS air
        ON a.`출발공항코드` = air.`항공사코드`
    INNER JOIN db_air.`항공사` AS air2
        ON a.`도착지공항코드` = air2.`항공사코드`
    GROUP BY a.`년도`, a.`월`, air.`도시`, air2.`도시`
) AS t
WHERE 순위 <= 5
ORDER BY t.`년도`, t.`월` ASC;

