from tools.t1_revision_resolver import RevisionResolver
from tools.t2_relink_across_projects import RelinkAcrossProjects
from tools.t3_smart_reframer import SmartReframer
from tools.t4_caption_layout_protector import CaptionLayoutProtector
from tools.t5_feedback_compiler import FeedbackCompiler
from tools.t6_timeline_normalizer import TimelineNormalizer
from tools.t7_component_graphics import ComponentGraphicsSystem
from tools.t8_delivery_spec_enforcer import DeliverySpecEnforcer
from tools.t9_change_impact_analyzer import ChangeImpactAnalyzer
from tools.t10_brand_drift_detector import BrandDriftDetector

TOOL_REGISTRY = {
    RevisionResolver.tool_id: RevisionResolver,
    RelinkAcrossProjects.tool_id: RelinkAcrossProjects,
    SmartReframer.tool_id: SmartReframer,
    CaptionLayoutProtector.tool_id: CaptionLayoutProtector,
    FeedbackCompiler.tool_id: FeedbackCompiler,
    TimelineNormalizer.tool_id: TimelineNormalizer,
    ComponentGraphicsSystem.tool_id: ComponentGraphicsSystem,
    DeliverySpecEnforcer.tool_id: DeliverySpecEnforcer,
    ChangeImpactAnalyzer.tool_id: ChangeImpactAnalyzer,
    BrandDriftDetector.tool_id: BrandDriftDetector,
}
