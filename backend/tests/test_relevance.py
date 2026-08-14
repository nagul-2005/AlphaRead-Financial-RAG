import unittest

from relevance import calibrate_bge_reranker_score


class BGERerankerCalibrationTests(unittest.TestCase):
    def test_sigmoid_output_is_not_displayed_as_a_match_percentage(self):
        # A 0.51 default-sigmoid score means a raw logit close to zero. It must
        # become low confidence after BGE's relevance-boundary calibration.
        self.assertEqual(
            calibrate_bge_reranker_score(0.51, score_is_probability=True),
            0.123
        )


    def test_high_raw_bge_logit_remains_high_confidence(self):
        self.assertEqual(calibrate_bge_reranker_score(4.0), 0.881)


    def test_missing_score_stays_missing(self):
        self.assertIsNone(calibrate_bge_reranker_score(None))
