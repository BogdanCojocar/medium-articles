FROM jupyter/pyspark-notebook:7f1482f5a136

RUN cd /usr/local/spark/jars && wget https://repo1.maven.org/maven2/ml/dmlc/xgboost4j/0.72/xgboost4j-0.72.jar
RUN cd /usr/local/spark/jars && wget https://repo1.maven.org/maven2/ml/dmlc/xgboost4j-spark/0.72/xgboost4j-spark-0.72.jar

RUN cd work/ && wget https://github.com/dmlc/xgboost/files/2161553/sparkxgb.zip

RUN pip install findspark