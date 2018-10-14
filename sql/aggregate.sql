SELECT
    institution_name,
    total
FROM (
    SELECT
        institution_niicode,
        SUM(1 / saimokusentakusuu) AS total
    FROM grantaward_field
        INNER JOIN grantaward USING (awardnumber)
        INNER JOIN kaken_master_field USING (field_path)  
    WHERE grantaward.startfiscalyear >= 2014
        AND grantaward.startfiscalyear <= 2017
        AND grantaward.category_niicode IN (60, 68, 69, 72, 64, 65, 75)
        AND grantaward_field.field_table = "saimoku"
        AND kaken_master_field.field_table_start_date = "2014-04-01"
        AND kaken_master_field.field_table_type = "saimoku"
        AND kaken_master_field.field_name = :bunka
AND kaken_master_field.layer = 3
GROUP BY institution_niicode
) A
INNER JOIN kaken_master_institution USING
(institution_niicode);
