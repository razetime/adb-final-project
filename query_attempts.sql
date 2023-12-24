-- SELECT delivery_city,delivery_district,COUNT(product_number)
-- FROM order_2011Q1
-- WHERE
--     EXTRACT(MONTH FROM order_establishment_time) = 1 AND 
--     product_number = 1199969
--     AND delivery_city='基隆'
-- GROUP BY delivery_city,delivery_district;

select count(distinct(supplier_name)) from supplier where supplier_registration_district='中正';

SELECT delivery_district, geom 
from order_2011q1, gadm41_twn_2
where delivery_district = left(nl_name_2,2) limit 5;
