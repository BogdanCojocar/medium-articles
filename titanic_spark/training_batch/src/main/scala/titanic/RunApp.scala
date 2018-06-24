package titanic

import ml.dmlc.xgboost4j.scala.spark.XGBoostEstimator
import org.apache.spark.ml.{Pipeline, PipelineModel}
import org.apache.spark.ml.feature.{StringIndexer, VectorAssembler}
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.types.{DoubleType, StringType, StructField, StructType}

object RunApp {

  def main(args: Array[String]): Unit = {

    // start the spark session
    val spark  = SparkSession.builder()
      .appName("Spark XGBOOST Titanic Training")
      .master("local[*]")
      .getOrCreate()

    // path where we have the training data
    val filePath = "file:///your_path/train.csv"
    val modelPath = "your_path"

    val schema = StructType(
      Array(StructField("PassengerId", DoubleType),
        StructField("Survival", DoubleType),
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

    // read the raw data
    val df_raw = spark
      .read
      .option("header", "true")
      .schema(schema)
      .csv(filePath)

    // fill all na values with 0
    val df = df_raw.na.fill(0)

    // convert nominal types to numeric for the columns, sex, cabin and embarked
    val sexIndexer = new StringIndexer()
      .setInputCol("Sex")
      .setOutputCol("SexIndex")
      .setHandleInvalid("keep")

    val cabinIndexer = new StringIndexer()
      .setInputCol("Cabin")
      .setOutputCol("CabinIndex")
      .setHandleInvalid("keep")

    val embarkedIndexer = new StringIndexer()
      .setInputCol("Embarked")
      .setOutputCol("EmbarkedIndex")
      .setHandleInvalid("keep")

    // create the feature vector
    val vectorAssembler = new VectorAssembler()
      .setInputCols(Array("Pclass", "SexIndex", "Age", "SibSp", "Parch", "Fare", "CabinIndex", "EmbarkedIndex"))
      .setOutputCol("features")

    // use the estimator to create the model
    val xgbEstimator = new XGBoostEstimator(Map[String, Any]("num_rounds" -> 100))
      .setFeaturesCol("features")
      .setLabelCol("Survival")

    // create the pipeline with the steps
    val pipeline = new Pipeline().setStages(Array(sexIndexer, cabinIndexer, embarkedIndexer, vectorAssembler, xgbEstimator))

    // create the model following the pipeline steps
    val cvModel = pipeline.fit(df)

    // save the model
    cvModel.write.overwrite.save(modelPath)






  }

}
