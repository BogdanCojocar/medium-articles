from src.jobs.pi import run, f
import pytest


def test_f():
    expected = 1

    assert pytest.approx(expected, 0.1) == f(100000)


def test_pi_run(spark_session):

    expected = 3.1438
    conf = {
        "partitions": 4
    }

    assert pytest.approx(expected, 0.01) == run(spark_session, conf)
