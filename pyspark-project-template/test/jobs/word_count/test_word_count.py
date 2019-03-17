from src.jobs.word_count import get_keyval, run


def test_get_keyval():
    words=['this', 'are', 'words', 'words']
    expected_results=[['this', 1], ['are', 1], ['words', 1], ['words', 1]]

    assert expected_results == get_keyval(words)


def test_word_count_run(spark_session):
    expected_results = [('one', 1), ('two', 1), ('three', 2), ('four', 2), ('test', 1)]
    conf = {
        'relative_path': '',
        'words_file_path': '/word_count/resources/word_count.csv'
    }

    assert expected_results == run(spark_session, conf)
