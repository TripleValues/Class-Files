use db_air;

-- `장거리노선` 테이블 drop
drop table db_air.`장거리노선`;


-- 1. `장거리노선` 테이블 생성 (1987년)
create TABLE db_air.`장거리노선` as
select 
    t.`출발지`,
    t.`도착지`,
    t.`년도`, 
    round(avg(cast(t.`도착지연시간` as signed)), 1) as 평균도착지연시간,
    t.`비행거리`
from(
	select 
		air1.`도시` as 출발지,
		air2.`도시` as 도착지,
		a.`년도`, 
	    a.`도착지연시간`,
	    a.`비행거리`
	from `비행` a
	inner join `항공사` as air1 
		on a.`출발공항코드` = air1.`항공사코드` 
	inner join `항공사` as air2 
		on a.`도착지공항코드` = air2.`항공사코드` 
	where a.`비행거리` regexp '^[0-9]+'
	and a.`도착지연시간` regexp '^[0-9]+'
	and a.`년도` = 1987
	and cast(a.`비행거리` as signed) > 2500
) t
group by t.`출발지`, t.`도착지`, t.`년도`, t.`비행거리`
order by cast(t.`비행거리` as signed) desc
;

-- 2. `장거리노선` 데이터 추가 (1988년)
insert into db_air.`장거리노선`
select 
    t.`출발지`,
    t.`도착지`,
    t.`년도`, 
    round(avg(cast(t.`도착지연시간` as signed)), 1) as 평균도착지연시간,
    t.`비행거리`
from(
	select 
		air1.`도시` as 출발지,
		air2.`도시` as 도착지,
		a.`년도`, 
	    a.`도착지연시간`,
	    a.`비행거리`
	from `비행` a
	inner join `항공사` as air1 
		on a.`출발공항코드` = air1.`항공사코드` 
	inner join `항공사` as air2 
		on a.`도착지공항코드` = air2.`항공사코드` 
	where a.`비행거리` regexp '^[0-9]+'
	and a.`도착지연시간` regexp '^[0-9]+'
	and a.`년도` = 1988
	and cast(a.`비행거리` as signed) > 2500
) t
group by t.`출발지`, t.`도착지`, t.`년도`, t.`비행거리`
order by cast(t.`비행거리` as signed) desc
;

-- 3. `장거리노선` 데이터 추가 (1989년)
insert into db_air.`장거리노선`
select 
    t.`출발지`,
    t.`도착지`,
    t.`년도`, 
    round(avg(cast(t.`도착지연시간` as signed)), 1) as 평균도착지연시간,
    t.`비행거리`
from(
	select 
		air1.`도시` as 출발지,
		air2.`도시` as 도착지,
		a.`년도`, 
	    a.`도착지연시간`,
	    a.`비행거리`
	from `비행` a
	inner join `항공사` as air1 
		on a.`출발공항코드` = air1.`항공사코드` 
	inner join `항공사` as air2 
		on a.`도착지공항코드` = air2.`항공사코드` 
	where a.`비행거리` regexp '^[0-9]+'
	and a.`도착지연시간` regexp '^[0-9]+'
	and a.`년도` = 1989
	and cast(a.`비행거리` as signed) > 2500
) t
group by t.`출발지`, t.`도착지`, t.`년도`, t.`비행거리`
order by cast(t.`비행거리` as signed) desc
;

-- 4. 묶어서 보기
SELECT
    concat(`출발지`, '→', `도착지`) as `운항노선`,
    `년도`,
    `평균도착지연시간`,
    `비행거리`
from db_air.`장거리노선`
order by `년도` desc, `비행거리` asc
;

-- 5. 장거리노선 년도별 평균의 평균 구하기 (노선수, 평균도착지연시간, 최대도착지연시간, 최대비행거리)
select 
    `년도`, 
    count(*) as `노선수`, -- 해당 년도의 장거리 노선이 몇 개인지
    round(avg(`평균도착지연시간`), 1) as `평균지연시간`, -- 노선들의 평균을 다시 평균 내기
    round(max(`평균도착지연시간`), 1) as `최대지연시간`,
    max(`비행거리`) as `최대비행거리` -- 그해 가장 멀리 간 거리
from db_air.`장거리노선`
group by `년도` -- 년도별로 그룹 묶기
order by `년도` asc
;

-- 6. 년도별 비행거리 상위 10개
create or replace view db_air.`장거리TOP10` as
with 장거리랭킹 as (
	select
		`출발지`,
        `도착지`,
        `년도`,
        `평균도착지연시간`,
        `비행거리`,
        row_number() over (partition by `년도` order by `비행거리` desc) as 순위
	from db_air.`장거리노선`
)
select
	`출발지`,
    `도착지`,
    `년도`,
    `평균도착지연시간`,
    `비행거리`
from 장거리랭킹
where `순위` <= 10
;
