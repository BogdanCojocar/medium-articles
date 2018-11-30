package com.app

import org.apache.spark.SparkConf
import org.apache.spark.sql.SparkSession

object RunBatchJob {

  def main(args: Array[String]): Unit = {

    val sparkConf = new SparkConf()

    sparkConf.set("spark.cassandra.connection.host", "YOUR_CASSANDRA_HOST")
    sparkConf.set("spark.cassandra.connection.port", "YOUR_CASSANDRA_PORT")

    val spark: SparkSession = SparkSession.builder()
      .appName("RunBatchJob")
      .config(sparkConf)
      .getOrCreate()

    import spark.implicits._

    spark.sparkContext.hadoopConfiguration.set("fs.s3a.acl.default", "BucketOwnerFullControl")

    val input = spark.read
      .format("org.apache.spark.sql.cassandra")
      .options(Map("table" -> "my_table", "keyspace" -> "my_schema"))
      .load()

    input
      .dropDuplicates
      .write
      .mode("append")
      .parquet("s3a://your_bucket/your_preffix/")
  }

}
