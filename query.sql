-- Write your custom SQL query here.
-- Example:
-- SELECT * FROM my_database.my_table LIMIT 1000;

-- Cross database example:
-- SELECT a.*, b.* FROM db1.table_a a JOIN db2.table_b b ON a.id = b.id;
SELECT
    * 
FROM
    SW_PBB.CPPMOD_PBB_SPPT_FINAL a
    JOIN SW_PBB.CPPMOD_TAX_KECAMATAN b ON a.CPM_OP_KECAMATAN = b.CPC_TKC_ID
    JOIN SW_PBB.CPPMOD_TAX_KELURAHAN c ON a.CPM_OP_KELURAHAN = c.CPC_TKL_ID 
WHERE
    a.CPM_NOP = a.CPM_WP_NO_KTP
    limit 100;