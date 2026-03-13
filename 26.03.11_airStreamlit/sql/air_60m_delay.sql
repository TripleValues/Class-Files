use db_air;

-- `60분이상_지연비행` 테이블 drop
DROP TABLE db_air.`60분이상_지연비행`;

-- `60분이상_지연비행` 테이블 정재?
CREATE TABLE db_air.`60분이상_지연비행` AS
SELECT 
  a.`년도`, a.`월`, a.`일`, a.`요일`,
  air.`항공사명` AS `출발항공사`, a.`항공편번호`, a.`도착지공항코드`, 
  air.`도시` AS `출발지공항`, airs.`도시` AS `도착지공항`,
  c.`설명` AS `운반대설명`,
  CAST(a.`도착지연시간` AS SIGNED) AS `도착지연시간`
FROM db_air.`비행` AS a
  INNER JOIN db_air.`항공사` AS air
    ON (a.`출발공항코드` = air.`항공사코드`)
  INNER JOIN db_air.`항공사` AS airs
    ON (a.`도착지공항코드` = airs.`항공사코드`)
  INNER JOIN db_air.`운반대` AS c
    ON (a.`출발공항코드` = c.`코드`)
WHERE a.`도착지연시간` REGEXP '^[0-9]+'
  AND CAST(a.`도착지연시간` AS SIGNED) >= 60
  AND a.`비행취소여부` = 0


-- 1987년 금요일의 도착지 Chicago 항공에 60분 이상 지연 도착한 TOP10  SELECT
SELECT 
  a.`년도`, a.`월`, a.`일`, w.`요일`,
  CONCAT(a.`출발지공항`, ' → ', a.`도착지공항`) AS `운항노선`,
  a.`운반대설명`,
  a.`도착지연시간`
FROM db_air.`60분이상_지연비행` AS a
  INNER JOIN db_air.`요일` AS w
    ON (a.`요일` = w.`코드`)
WHERE `도착지공항코드` = 'ORD'
  AND a.`년도` = 1987
  AND a.`요일` = 5
GROUP BY a.`도착지연시간`, a.`년도`, a.`월`, a.`일`
ORDER BY a.`도착지연시간` DESC, a.`년도` DESC, a.`월` ASC, a.`일` ASC
LIMIT 10;