package titanic

import org.apache.spark.sql.execution.streaming.Sink
import org.apache.spark.sql.{DataFrame, SQLContext}
import org.apache.spark.sql.sources.StreamSinkProvider
import org.apache.spark.sql.streaming.OutputMode

// define the sink provider
abstract class MLSinkProvider extends StreamSinkProvider {
  def process(df: DataFrame): Unit

  def createSink(
                  sqlContext: SQLContext,
                  parameters: Map[String, String],
                  partitionColumns: Seq[String],
                  outputMode: OutputMode): MLSink = {
    new MLSink(process)
  }
}

// define the custom sink
case class MLSink(process: DataFrame => Unit) extends Sink {
  override def addBatch(batchId: Long, data: DataFrame): Unit = {
    process(data)
  }
}