########################################################################
# PURPOSE: TO PERFORM THE AGGREGATION FOR THE PO_CO_ITM_VNDR_DAY_AGGR   #
# 1010 name: AGR_VNDR_AGR_TRANS_RESEG
########################################################################

import sys
import time
import logging
import datetime
import os.path
import traceback
from pyspark import StorageLevel
from pyspark.sql import HiveContext
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext

sys.path.append('../')
sys.path.append('/home/hadoop/')
import common.config as config

import common_func_RSALAZAR as common_func
import RevManEarnedIncomeQueries as sqlfile

#PENDING RESTORE TO ORIGINAL CODE import common.common_func_RSALAZAR as common_func
#ON HOLD USING QUERY FILE - PENDING import po_co_itm_vndr_day_aggr_sql as query_file


def main():

    #PENDING Try Sending output to screen

    # To fetch the current date and script name from sys.argv[] and generate log file path.
    current_date = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    file_name = sys.argv[0].split('/')[-1].split('.')[0]

    log_file_path = "{}/{}_{}.log".format(config.log_file_directory, file_name, current_date)


    # To initialize logging
    #cHANGED FROM INFO to WARNING.
    logging.basicConfig(filename=log_file_path, filemode='w', level=logging.ERROR)

    logging.info('\n##################  Mapping Logic Started at %s ##################', datetime.datetime.now())

    if len(sys.argv) > 1:
        co_nbrs = sys.argv[1].split(',')
        co_nbr_list = ', '.join("'{0}'".format(co_nbr.zfill(3)) for co_nbr in co_nbrs)
        logging.info('Company Number - %s', co_nbr_list)

    else:
        co_nbr_list = "'000'"
        logging.info("Company Number is not passed as argument. Script will process data for all OpCo's")

    # calling initializeSparkHiveContext() function from common_func.py to initialize spark session, register spark and hive context.
    #pending replace later hive_context = common_func.initializeSparkHiveContext('VendorAgreements')

    #---------------------------------------------------------------------------------------------------
    from pyspark.sql import HiveContext
    from pyspark.sql import SparkSession
    from pyspark.sql import SQLContext

    spark = SparkSession.builder.master("yarn").appName("VendorAgreements").config("spark.serializer",
                                                                                 "org.apache.spark.serializer.KryoSerializer").config(
        "spark.kryoserializer.buffer.max", "126mb").enableHiveSupport().getOrCreate()
    sc = spark.sparkContext
    hive_context = HiveContext(sc)

    # Control the logs to the stdout (console)
    # Other     options     for Level include: all, debug, error, fatal, info, off, trace, trace_int, warn
    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org").setLevel(logger.Level.ERROR)
    logger.LogManager.getLogger("akka").setLevel(logger.Level.ERROR)

    # ---------------------------------------------------------------------------------------------------

    logging.info('\n##################  Mapping Logic Started at %s ##################', datetime.datetime.now())

    logging.info('Assigning values Started at  %s', datetime.datetime.now())

    df_vendor_agr = common_func.registerRedshiftQuery(hive_context, sqlfile.SqlVendorAgreement, "TMP_SQL_agr_vndr_agr_trans_fact")

    # RETURNED/REGISTERED NAME IS rs_TMP_SQL_agr_vndr_agr_trans_fact_mstr

    df1_count_all = hive_context.sql("SELECT count(*) COUNT__agr_vndr_agr_trans_fact FROM rs_TMP_SQL_agr_vndr_agr_trans_fact_mstr")

    print("********************************SHOW*******************************************")
    df1_count_all.show()

    print("********************************SCHEMA*******************************************")
    df_vendor_agr.printSchema()
    # Count using Select statement
    # TEMPLATE EXAMPLE countDistinctDF_sql = sqlContext.sql("SELECT firstName, lastName, count(distinct firstName) as distinct_first_names FROM databricks_df_example GROUP BY firstName, lastName")


    ##The tempdir values is tempdir="s3://sysco-nonprod-seed-spark-redshift-temp/
    print("***step 1 before writing***")
    # need to call function insertDataFrameToS3(dataframe_name, path)
    # sample call common_func.loadDataIntoRedshift(logging, 'CUSTOM', config.dataMartSchema, 'PO_UNIQUE', PO_UNIQUE_INSERT_DATA_FRAME,    co_nbr_list, preaction_query=preaction_query)

    #PARAMETERS ARE:
    # param1=logging
    # param2='INSERT','UPSERT'
    # param3=schema (intp value for stageSchema)
    # param4=table_name (final destination)
    # param5=dataframe

    print("***Prepare Company List***")
    co_nbr_list = "'000'"

    print("***Insert Statements ***")
    common_func.loadDataIntoRedshift(logging, 'INSERT', config.stageSchema, 'EI_AGR_VNDR_AGR_TRANS_RESEG', df_vendor_agr , opco_list=co_nbr_list)

    print("********************************THE END  *******************************************")

    logging.info('**********************************************', datetime.datetime.now())
    logging.info('Script read01_afr_vendor_enterprise completed %s', datetime.datetime.now())

#Pending persist

if __name__ == "__main__":
    try:
        main()
    except BaseException as error:
        logging.error(traceback.format_exc())
        raise

