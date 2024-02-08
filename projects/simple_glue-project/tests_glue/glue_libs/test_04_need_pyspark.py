# -*- coding: utf-8 -*-

"""
This example depends on your custom Glue Python Library, and it might depends on
other 3rd party library.
"""

# Create SparkContext
from pyspark.sql import SparkSession, DataFrame
from simple_glue.glue_libs.pyspark_utils import double_a_column


def test():
    spark_ses = SparkSession.builder.getOrCreate()
    df: DataFrame = spark_ses.createDataFrame(
        [
            ("a", 1),
            ("b", 2),
            ("c", 3),
        ],
        ("id", "value"),
    )
    df1 = double_a_column(df, df.value, "value")
    assert list(df1.select("value").toPandas()["value"]) == [2, 4, 6]
    print("")
    df1.show()


if __name__ == "__main__":
    from simple_glue.tests.glue import run_unit_test

    run_unit_test(__file__, glue_version="4.0")
