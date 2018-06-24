package titanic

import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.types._

// define the processing in the sink
class XGBoostMLSinkProvider extends MLSinkProvider {
  override def process(df: DataFrame) {
    XGBoostModel.transform(df)
  }
}

object RunApp {

  def main(args: Array[String]): Unit = {

    // the directory where we store the testing csv file
    val fileDir = "your_dir"
    val checkpoint_location = "your_location"

    // define the spark session
    val spark: SparkSession = SparkSession.builder()
      .appName("Spark Structured Streaming XGBOOST")
      .master("local[*]")
      .getOrCreate()

    // define the schema of the csv file
    val schema = StructType(
      Array(StructField("PassengerId", DoubleType),
        StructField("Pclass", DoubleType),
        StructField("Name", StringType),
        StructField("Sex", StringType),
        StructField("Age", DoubleType),
        StructField("SibSp", DoubleType),
        StructField("Parch", DoubleType),
        StructField("Ticket", StringType),
        StructField("Fare", DoubleType),
        StructField("Cabin", StringType),
        StructField("Embarked", StringType)
      ))

      // read the csv test data in a realtime df
      val df = spark
        .readStream
        .option("header", "true")
        .schema(schema)
        .csv(fileDir)

      // start writing the data in our custom sink
      df.writeStream
        .format("titanic.XGBoostMLSinkProvider")
        .queryName("XGBoostQuery")
        .option("checkpointLocation", checkpoint_location)
        .start()

    // wait for query to terminate
    spark.streams.awaitAnyTermination()
  }
}
