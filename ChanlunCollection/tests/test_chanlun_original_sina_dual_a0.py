import unittest,json
from copy import deepcopy
from tools.audit_chanlun_original_sina_dual_a0 import audit,SPEC,REPORT
class OriginalSinaA0(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=json.loads(SPEC.read_text(encoding="utf-8"));cls.r=REPORT.read_text(encoding="utf-8")
 def reject(self,change):
  s=deepcopy(self.s);change(s)
  with self.assertRaises(ValueError):audit(s,self.r)
 def test_author_main_posts(self):
  self.assertEqual(audit(self.s,self.r)["author_main_posts"],2)
 def test_original_july19_source_id(self):
  self.reject(lambda s:s["primary_posts"][0].update(url="https://example.org/a"))
 def test_original_july20_date(self):
  self.reject(lambda s:s["primary_posts"][1].update(date="2007-07-19 15:29:28"))
 def test_main_body_not_secondary_reply(self):
  self.reject(lambda s:s["primary_posts"][1].update(role="THIRD_PARTY_COMMENT"))
 def test_exact_author_source_claim(self):
  self.reject(lambda s:s["course_anchors"][6].update(id="INVENTED_SOURCE"))
 def test_original_source_page(self):
  self.reject(lambda s:s["course_anchors"][3].update(pages=[9000]))
 def test_do_not_promote_pen_to_movement(self):
  self.reject(lambda s:s["type_contract"].update(strict_segment_is_subordinate_finished_movement=True))
 def test_do_not_promote_tick_to_movement(self):
  self.reject(lambda s:s["type_contract"].update(actual_trade_is_subordinate_finished_movement=True))
 def test_no_segment_end_equivalence(self):
  self.reject(lambda s:s["type_contract"].update(a_segment_finish_proves_movement_finish=True))
 def test_practical_can_construct_minimum_center(self):
  self.reject(lambda s:s["type_contract"].update(practical_segments_may_build_lowest_center=False))
 def test_no_universal_equal_market_outputs(self):
  self.reject(lambda s:s["type_contract"].update(universal_equal_center_outputs_from_same_recurrence=True))
 def test_no_complete_asof_original_parser_claim(self):
  self.reject(lambda s:s["type_contract"].update(source_author_proved_a_complete_asof_market_parser=True))
 def test_same_f_different_a0_toy(self):
  self.reject(lambda s:s["toy_logic"].update(practical_a1=1))
 def test_theory_actual_trades(self):
  self.reject(lambda s:s["type_contract"].update(strict_a0_source="FRACTAL_PEN_SEGMENT_CONSTRUCTION"))
 def test_practical_formal_fractal_pen_segment(self):
  self.reject(lambda s:s["type_contract"].update(practical_a0_source="INDIVIDUAL_TRANSACTION_EXECUTIONS"))
 def test_expert_post_still_missing(self):
  self.reject(lambda s:s["scope_limits"].update(original_expert_public_post_verified=True))
 def test_original_html_bytes_not_authenticated(self):
  self.reject(lambda s:s["scope_limits"].update(original_2007_sina_post_bytes_authenticated=True))
 def test_original_diagram_pixels_not_verified(self):
  self.reject(lambda s:s["scope_limits"].update(original_jul19_chart_pixels_verified=True))
 def test_ob38_still_open(self):
  self.reject(lambda s:s["open"].remove("OB38_OPEN"))
 def test_no_real_market(self):
  self.reject(lambda s:s["scope_limits"].update(historical_market_ticks_replayed=True))
if __name__=="__main__":unittest.main()
