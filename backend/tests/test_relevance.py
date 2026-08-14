import unittest

from relevance import calibrate_bge_reranker_score, fastembed_relevance_score


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

    def test_fastembed_rejects_a_single_generic_term_match(self):
        score = fastembed_relevance_score(
            "Who is the President of India?",
            "A PAN card supports tax transactions in India for NRIs and OCIs.",
            0.496,
        )
        self.assertLess(score, 0.35)

    def test_fastembed_keeps_a_multi_term_pan_citizenship_match(self):
        score = fastembed_relevance_score(
            "How can citizenship information be updated for a PAN card?",
            "To change citizenship in a PAN card, notify the assessing officer.",
            0.496,
        )
        self.assertGreaterEqual(score, 0.35)
