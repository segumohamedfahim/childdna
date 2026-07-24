"""Prediction Service - Deterministic Heuristic AI Intelligence Engine"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.child import ChildRepository
from app.repositories.guardian import GuardianRepository
from app.repositories.rescue_session import RescueSessionRepository
from app.repositories.reunion_record import ReunionRecordRepository
from app.repositories.incident_analysis import IncidentAnalysisRepository
from app.repositories.incident_match import IncidentMatchRepository
from app.repositories.alert import AlertRepository
from app.schemas.prediction import (
    PredictionMetadata,
    ReunionPredictionResponse,
    RescuePredictionResponse,
    IncidentRiskResponse,
    AlertPredictionResponse,
    PriorityPredictionResponse,
    AISummaryResponse,
    AISummarySection,
    RecommendationItem,
    RecommendationResponse,
    PredictionHealthResponse,
)
from app.utils.logger import logger


class PredictionService:
    """Deterministic heuristic prediction and intelligence engine.

    All predictions are rule-based heuristics. No machine learning,
    no LLM, no external APIs. Everything is reproducible.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.child_repo = ChildRepository(session)
        self.guardian_repo = GuardianRepository(session)
        self.rescue_repo = RescueSessionRepository(session)
        self.reunion_repo = ReunionRecordRepository(session)
        self.analysis_repo = IncidentAnalysisRepository(session)
        self.match_repo = IncidentMatchRepository(session)
        self.alert_repo = AlertRepository(session)

    async def predict_reunion_probability(
        self, child_id: str,
    ) -> ReunionPredictionResponse:
        """Predict the probability of a child being reunited.

        Uses heuristic scoring based on existing rescue data,
        guardian status, and rescue history.

        Args:
            child_id: The child UUID.

        Returns:
            ReunionPredictionResponse: Prediction with probability and factors.
        """
        now = datetime.now(timezone.utc)
        factors: list[str] = []
        score = 0.5  # Base probability

        child = await self.child_repo.get_by_id(child_id)
        if not child:
            return ReunionPredictionResponse(
                metadata=PredictionMetadata(generated_at=now),
                child_id=child_id,
                reunion_probability=0.0,
                confidence="low",
                factors=["Child not found in system"],
                explanation="No data available for prediction.",
                recommended_actions=["Register child in the system"],
            )

        guardian = await self.guardian_repo.get_by_id(child.guardian_id)
        rescues = await self.rescue_repo.get_by_child(child_id)
        reunions = await self.reunion_repo.get_by_child(child_id)

        # Guardian availability
        if guardian and guardian.is_active:
            score += 0.15
            factors.append("Active guardian registered")
        else:
            score -= 0.15
            factors.append("No active guardian found")

        # Rescue history
        if rescues:
            active = sum(1 for r in rescues if r.status and r.status.value in ("pending", "active"))
            completed = sum(1 for r in rescues if r.status and r.status.value == "complete")
            if completed > 0:
                score += 0.1
                factors.append(f"{completed} completed rescue(s)")
            if active > 0:
                score -= 0.1
                factors.append(f"{active} active rescue(s)")
        else:
            factors.append("No rescue history")

        # Previous reunions
        if reunions:
            score += 0.15
            factors.append(f"{len(reunions)} previous reunion(s)")
        else:
            factors.append("No previous reunions")

        # Child status
        if child.status and child.status.value == "active":
            score += 0.05
        else:
            score -= 0.05

        score = max(0.0, min(1.0, score))
        confidence = self._score_to_confidence(score)

        explanation = (
            f"Reunion probability based on guardian status, "
            f"rescue history, and previous reunions."
        )

        actions = self._build_reunion_actions(score, guardian, rescues)

        return ReunionPredictionResponse(
            metadata=PredictionMetadata(generated_at=now),
            child_id=child_id,
            reunion_probability=round(score, 2),
            confidence=confidence,
            factors=factors,
            explanation=explanation,
            recommended_actions=actions,
        )

    async def predict_rescue_success(
        self, rescue_session_id: str,
    ) -> RescuePredictionResponse:
        """Predict the success probability of a rescue session.

        Args:
            rescue_session_id: The rescue session UUID.

        Returns:
            RescuePredictionResponse: Prediction with probability and factors.
        """
        now = datetime.now(timezone.utc)
        factors: list[str] = []
        score = 0.5

        rescue = await self.rescue_repo.get_by_id(rescue_session_id)
        if not rescue:
            return RescuePredictionResponse(
                metadata=PredictionMetadata(generated_at=now),
                rescue_session_id=rescue_session_id,
                success_probability=0.0,
                confidence="low",
                factors=["Rescue session not found"],
                explanation="No data available for prediction.",
                recommended_actions=[],
            )

        # Status-based factors
        if rescue.status:
            if rescue.status.value == "complete":
                score += 0.3
                factors.append("Rescue already completed")
            elif rescue.status.value == "cancelled":
                score -= 0.3
                factors.append("Rescue was cancelled")
            elif rescue.status.value == "active":
                score += 0.1
                factors.append("Rescue is in progress")

        # Priority-based factors
        if rescue.priority:
            if rescue.priority <= 1:
                score += 0.1
                factors.append("High priority rescue")
            elif rescue.priority >= 3:
                score -= 0.1
                factors.append("Low priority rescue")

        # Rescuer availability
        if rescue.rescuer_name:
            score += 0.1
            factors.append("Rescuer assigned")
        else:
            score -= 0.1
            factors.append("No rescuer assigned")

        # Location information
        if rescue.latitude and rescue.longitude:
            score += 0.1
            factors.append("Location coordinates available")
        else:
            score -= 0.05
            factors.append("No location data")

        # Duration-based factor
        estimated_hours = None
        if rescue.started_at and not rescue.ended_at:
            elapsed = (now - rescue.started_at).total_seconds() / 3600
            if elapsed > 24:
                score -= 0.1
                factors.append(f"Rescue ongoing for {elapsed:.1f}h")

        if rescue.ended_at:
            estimated_hours = 0

        score = max(0.0, min(1.0, score))
        confidence = self._score_to_confidence(score)

        explanation = (
            f"Success probability calculated from rescue status, "
            f"priority level, rescuer assignment, and location data."
        )

        return RescuePredictionResponse(
            metadata=PredictionMetadata(generated_at=now),
            rescue_session_id=rescue_session_id,
            success_probability=round(score, 2),
            confidence=confidence,
            factors=factors,
            explanation=explanation,
            recommended_actions=[],
            estimated_completion_hours=estimated_hours,
        )

    async def predict_incident_risk(
        self, child_id: str,
    ) -> IncidentRiskResponse:
        """Assess the risk level for a child based on history.

        Args:
            child_id: The child UUID.

        Returns:
            IncidentRiskResponse: Risk assessment with score and factors.
        """
        now = datetime.now(timezone.utc)
        factors: list[str] = []
        risk = 0.0

        child = await self.child_repo.get_by_id(child_id)
        if not child:
            return IncidentRiskResponse(
                metadata=PredictionMetadata(generated_at=now),
                child_id=child_id,
                risk_level="unknown",
                risk_score=0.0,
                factors=["Child not found"],
                explanation="No data available.",
                recommended_actions=["Register child"],
            )

        rescues = await self.rescue_repo.get_by_child(child_id)
        analyses = await self.analysis_repo.get_all()

        # Number of incidents
        if len(rescues) >= 5:
            risk += 0.3
            factors.append(f"High incident count: {len(rescues)}")
        elif len(rescues) >= 2:
            risk += 0.15
            factors.append(f"Multiple incidents: {len(rescues)}")

        # Active incidents
        active = sum(1 for r in rescues if r.status and r.status.value in ("pending", "active"))
        if active > 0:
            risk += 0.2
            factors.append(f"{active} active incident(s)")

        # Guardian status
        guardian = await self.guardian_repo.get_by_id(child.guardian_id)
        if not guardian or not guardian.is_active:
            risk += 0.15
            factors.append("No active guardian")

        # Child status
        if child.status and child.status.value in ("inactive", "suspended"):
            risk += 0.1
            factors.append(f"Child status: {child.status.value}")

        risk = max(0.0, min(1.0, risk))

        risk_level = "low"
        if risk >= 0.6:
            risk_level = "high"
        elif risk >= 0.3:
            risk_level = "medium"

        explanation = (
            f"Risk assessment based on incident history, "
            f"active incidents, guardian status, and child status."
        )

        return IncidentRiskResponse(
            metadata=PredictionMetadata(generated_at=now),
            child_id=child_id,
            risk_level=risk_level,
            risk_score=round(risk, 2),
            factors=factors,
            explanation=explanation,
            recommended_actions=self._build_risk_actions(risk_level),
        )

    async def predict_alert_probability(
        self, incident_analysis_id: str,
    ) -> AlertPredictionResponse:
        """Predict the probability of an alert being generated.

        Args:
            incident_analysis_id: The incident analysis UUID.

        Returns:
            AlertPredictionResponse: Prediction with probability and factors.
        """
        now = datetime.now(timezone.utc)
        factors: list[str] = []
        score = 0.3

        analysis = await self.analysis_repo.get_by_id(incident_analysis_id)
        if not analysis:
            return AlertPredictionResponse(
                metadata=PredictionMetadata(generated_at=now),
                incident_analysis_id=incident_analysis_id,
                alert_probability=0.0,
                confidence="low",
                factors=["Analysis not found"],
                explanation="No data available.",
                recommended_actions=[],
            )

        # Confidence-based
        if analysis.overall_confidence >= 0.8:
            score += 0.3
            factors.append("High confidence analysis")
        elif analysis.overall_confidence >= 0.5:
            score += 0.15
            factors.append("Medium confidence analysis")
        else:
            score -= 0.1
            factors.append("Low confidence analysis")

        # Attribute completeness
        attr_count = 0
        if analysis.gender:
            attr_count += 1
        if analysis.estimated_age_min:
            attr_count += 1
        if analysis.emotion:
            attr_count += 1
        if analysis.clothing:
            attr_count += 1
        if analysis.location:
            attr_count += 1
        if analysis.distinguishing_features:
            attr_count += 1

        if attr_count >= 4:
            score += 0.2
            factors.append(f"Rich attribute set ({attr_count}/6)")
        elif attr_count >= 2:
            score += 0.1
            factors.append(f"Partial attribute set ({attr_count}/6)")
        else:
            score -= 0.1
            factors.append("Sparse attribute set")

        score = max(0.0, min(1.0, score))
        confidence = self._score_to_confidence(score)

        explanation = (
            f"Alert probability based on analysis confidence "
            f"and attribute completeness."
        )

        return AlertPredictionResponse(
            metadata=PredictionMetadata(generated_at=now),
            incident_analysis_id=incident_analysis_id,
            alert_probability=round(score, 2),
            confidence=confidence,
            factors=factors,
            explanation=explanation,
            recommended_actions=[],
        )

    async def generate_priority_score(
        self, incident_analysis_id: str,
    ) -> PriorityPredictionResponse:
        """Generate a priority score for an incident analysis.

        Args:
            incident_analysis_id: The incident analysis UUID.

        Returns:
            PriorityPredictionResponse: Priority score with level.
        """
        now = datetime.now(timezone.utc)
        factors: list[str] = []
        score = 0.0

        analysis = await self.analysis_repo.get_by_id(incident_analysis_id)
        if not analysis:
            return PriorityPredictionResponse(
                metadata=PredictionMetadata(generated_at=now),
                incident_analysis_id=incident_analysis_id,
                priority_score=0.0,
                priority_level="low",
                factors=["Analysis not found"],
                explanation="No data available.",
                recommended_actions=[],
            )

        # Confidence contributes up to 0.4
        if analysis.overall_confidence:
            score += analysis.overall_confidence * 0.4
            if analysis.overall_confidence >= 0.7:
                factors.append("High analysis confidence")
            elif analysis.overall_confidence >= 0.4:
                factors.append("Medium analysis confidence")

        # Age estimate contributes up to 0.2 (younger = higher priority)
        if analysis.estimated_age_min is not None:
            if analysis.estimated_age_min <= 5:
                score += 0.2
                factors.append("Very young child (0-5 years)")
            elif analysis.estimated_age_min <= 12:
                score += 0.1
                factors.append("Young child (6-12 years)")

        # Emotion contributes up to 0.2
        if analysis.emotion:
            distress_emotions = {"distressed", "fearful", "injured", "angry"}
            if analysis.emotion.lower() in distress_emotions:
                score += 0.2
                factors.append(f"Child in distress ({analysis.emotion})")
            else:
                score += 0.05
                factors.append(f"Child emotion: {analysis.emotion}")

        # Clothing data contributes to identification priority
        if analysis.clothing:
            score += 0.1
            factors.append("Clothing description available")

        # Features
        if analysis.distinguishing_features:
            score += 0.1
            factors.append("Distinguishing features documented")

        score = max(0.0, min(1.0, score))
        priority_level = "low"
        if score >= 0.7:
            priority_level = "critical"
        elif score >= 0.5:
            priority_level = "high"
        elif score >= 0.3:
            priority_level = "medium"

        explanation = (
            f"Priority calculated from analysis confidence, "
            f"child age, emotional state, and available attributes."
        )

        return PriorityPredictionResponse(
            metadata=PredictionMetadata(generated_at=now),
            incident_analysis_id=incident_analysis_id,
            priority_score=round(score, 2),
            priority_level=priority_level,
            factors=factors,
            explanation=explanation,
            recommended_actions=self._build_priority_actions(priority_level),
        )

    async def generate_ai_summary(
        self, entity_id: str, summary_type: str,
    ) -> AISummaryResponse:
        """Generate a structured AI summary for an entity.

        Args:
            entity_id: UUID of the entity.
            summary_type: Type (incident, rescue, child, guardian, reunion).

        Returns:
            AISummaryResponse: Structured summary with sections.
        """
        now = datetime.now(timezone.utc)
        sections: list[AISummarySection] = []
        observations: list[str] = []
        concerns: list[str] = []
        actions: list[str] = []
        overall = ""
        confidence = "medium"

        if summary_type == "child":
            child = await self.child_repo.get_by_id(entity_id)
            if not child:
                return self._empty_summary(entity_id, summary_type, now)
            guardian = await self.guardian_repo.get_by_id(child.guardian_id)
            rescues = await self.rescue_repo.get_by_child(entity_id)
            reunions = await self.reunion_repo.get_by_child(entity_id)

            overall = (
                f"Child {child.full_name} is "
                f"{'active' if child.status and child.status.value == 'active' else 'inactive'}. "
                f"Has {len(rescues)} rescue incident(s) and "
                f"{len(reunions)} reunion(s)."
            )
            sections.append(AISummarySection(
                heading="Child Profile",
                content=f"Name: {child.full_name}, Status: {child.status.value if child.status else 'unknown'}, "
                        f"Gender: {child.gender or 'not specified'}"
            ))
            if guardian:
                sections.append(AISummarySection(
                    heading="Guardian Information",
                    content=f"Guardian: {guardian.full_name}, Email: {guardian.email}, "
                            f"Active: {'Yes' if guardian.is_active else 'No'}"
                ))
            if rescues:
                active = sum(1 for r in rescues if r.status and r.status.value in ("pending", "active"))
                completed = sum(1 for r in rescues if r.status and r.status.value == "complete")
                sections.append(AISummarySection(
                    heading="Rescue History",
                    content=f"Total: {len(rescues)}, Active: {active}, Completed: {completed}"
                ))
            observations.append(f"Child has {len(rescues)} incident(s)")
            if len(rescues) >= 3:
                concerns.append("Multiple incidents suggest elevated risk")
            if not guardian or not guardian.is_active:
                concerns.append("Guardian is not active")

        elif summary_type == "incident":
            analysis = await self.analysis_repo.get_by_id(entity_id)
            if not analysis:
                return self._empty_summary(entity_id, summary_type, now)
            rescue = await self.rescue_repo.get_by_id(analysis.incident_id)
            overall = (
                f"Incident analysis confidence: {analysis.overall_confidence:.0%}. "
                f"Engine: {analysis.analysis_engine}."
            )
            sections.append(AISummarySection(
                heading="Analysis Details",
                content=f"Confidence: {analysis.overall_confidence:.2f}, "
                        f"Gender: {analysis.gender or 'N/A'}, "
                        f"Age: {analysis.estimated_age_min or '?'}-{analysis.estimated_age_max or '?'}"
            ))
            observations.append(f"Analysis confidence: {analysis.overall_confidence:.2f}")
            if analysis.overall_confidence < 0.4:
                concerns.append("Low confidence — verify with additional data")

        elif summary_type == "rescue":
            rescue = await self.rescue_repo.get_by_id(entity_id)
            if not rescue:
                return self._empty_summary(entity_id, summary_type, now)
            overall = f"Rescue session status: {rescue.status.value if rescue.status else 'unknown'}."
            sections.append(AISummarySection(
                heading="Rescue Details",
                content=f"Priority: {rescue.priority}, Rescuer: {rescue.rescuer_name or 'Unassigned'}"
            ))

        elif summary_type == "guardian":
            guardian = await self.guardian_repo.get_by_id(entity_id)
            if not guardian:
                return self._empty_summary(entity_id, summary_type, now)
            overall = f"Guardian {guardian.full_name} is {'active' if guardian.is_active else 'inactive'}."
            sections.append(AISummarySection(
                heading="Guardian Profile",
                content=f"Name: {guardian.full_name}, Email: {guardian.email}, "
                        f"Phone: {guardian.phone or 'N/A'}"
            ))

        elif summary_type == "reunion":
            reunion = await self.reunion_repo.get_by_id(entity_id)
            if not reunion:
                return self._empty_summary(entity_id, summary_type, now)
            overall = f"Reunion completed at {reunion.reunion_time.isoformat() if reunion.reunion_time else 'unknown'}."
            sections.append(AISummarySection(
                heading="Reunion Details",
                content=f"Guardian: {reunion.guardian_name}, Rescuer: {reunion.rescuer_name}, "
                        f"Method: {reunion.verification_method}"
            ))

        return AISummaryResponse(
            metadata=PredictionMetadata(generated_at=now),
            summary_type=summary_type,
            entity_id=entity_id,
            overall_assessment=overall,
            key_observations=observations,
            potential_concerns=concerns,
            confidence_level=confidence,
            recommended_next_actions=actions,
            sections=sections,
        )

    async def generate_recommendations(
        self, entity_id: str, entity_type: str,
    ) -> RecommendationResponse:
        """Generate rule-based recommendations for an entity.

        Args:
            entity_id: UUID of the entity.
            entity_type: Type (child, incident, rescue, guardian, analysis).

        Returns:
            RecommendationResponse: List of recommendations.
        """
        now = datetime.now(timezone.utc)
        recommendations: list[RecommendationItem] = []

        if entity_type == "analysis":
            analysis = await self.analysis_repo.get_by_id(entity_id)
            if analysis:
                matches = await self.match_repo.get_by_incident(
                    str(analysis.incident_id)
                )
                if analysis.overall_confidence >= 0.7:
                    recommendations.append(RecommendationItem(
                        recommendation="High confidence match — initiate guardian verification immediately",
                        priority="high",
                        reason="Analysis confidence exceeds 70% threshold",
                        confidence=0.9,
                    ))
                if matches:
                    high_matches = sum(
                        1 for m in matches
                        if m.match_category in ("identical", "very_high")
                    )
                    if high_matches >= 2:
                        recommendations.append(RecommendationItem(
                            recommendation="Multiple duplicate incidents detected — suggest merge review",
                            priority="high",
                            reason=f"{high_matches} high-confidence matches found",
                            confidence=0.85,
                        ))

        elif entity_type == "rescue":
            rescue = await self.rescue_repo.get_by_id(entity_id)
            if rescue and rescue.started_at:
                duration = (now - rescue.started_at).total_seconds() / 3600
                if duration > 24 and rescue.status and rescue.status.value not in ("complete", "cancelled"):
                    recommendations.append(RecommendationItem(
                        recommendation="Long rescue duration — recommend supervisor escalation",
                        priority="medium",
                        reason=f"Rescue ongoing for {duration:.1f} hours",
                        confidence=0.7,
                    ))

        elif entity_type == "child":
            child = await self.child_repo.get_by_id(entity_id)
            if child:
                guardian = await self.guardian_repo.get_by_id(child.guardian_id)
                if not guardian or not guardian.is_active:
                    recommendations.append(RecommendationItem(
                        recommendation="Child missing active guardian — recommend guardian registration",
                        priority="high",
                        reason="No active guardian linked to child",
                        confidence=0.8,
                    ))

        return RecommendationResponse(
            metadata=PredictionMetadata(generated_at=now),
            entity_id=entity_id,
            entity_type=entity_type,
            recommendations=recommendations,
        )

    async def get_prediction_health(self) -> PredictionHealthResponse:
        """Return health status of the prediction AI platform.

        Returns:
            PredictionHealthResponse: Health status.
        """
        now = datetime.now(timezone.utc)
        return PredictionHealthResponse(
            metadata=PredictionMetadata(generated_at=now),
            prediction_engine_status="operational",
            recommendation_engine_status="operational",
            summary_engine_status="operational",
            ai_version="1.0",
            supported_modules=[
                "reunion_prediction",
                "rescue_prediction",
                "incident_risk",
                "alert_prediction",
                "priority_scoring",
                "ai_summary",
                "recommendation_engine",
                "system_health",
            ],
            timestamp=now,
        )

    @staticmethod
    def _score_to_confidence(score: float) -> str:
        """Map a probability score to a confidence label."""
        if score >= 0.7:
            return "high"
        if score >= 0.4:
            return "medium"
        return "low"

    @staticmethod
    def _build_reunion_actions(
        score: float, guardian, rescues: list,
    ) -> list[str]:
        """Build recommended actions for reunion prediction."""
        actions = []
        if score < 0.4:
            actions.append("Register child in the system")
            actions.append("Assign a social worker")
        if not guardian or not guardian.is_active:
            actions.append("Locate and verify guardian")
        if not rescues:
            actions.append("Create a rescue incident")
        if 0.4 <= score < 0.7:
            actions.append("Update child profile information")
            actions.append("Contact local authorities")
        if score >= 0.7:
            actions.append("Prepare for reunification process")
            actions.append("Notify guardian immediately")
        if not actions:
            actions.append("Continue monitoring")
        return actions

    @staticmethod
    def _build_risk_actions(risk_level: str) -> list[str]:
        """Build recommended actions based on risk level."""
        if risk_level == "high":
            return [
                "Immediate intervention required",
                "Assign case worker",
                "Increase monitoring frequency",
                "Contact local authorities",
            ]
        if risk_level == "medium":
            return [
                "Schedule follow-up assessment",
                "Review incident history",
                "Update safety plan",
            ]
        return ["Continue routine monitoring", "No immediate action required"]

    @staticmethod
    def _build_priority_actions(priority_level: str) -> list[str]:
        """Build recommended actions based on priority level."""
        if priority_level == "critical":
            return [
                "Immediate response required",
                "Allocate resources",
                "Notify senior authorities",
            ]
        if priority_level == "high":
            return [
                "Prioritize response",
                "Assign experienced team",
            ]
        if priority_level == "medium":
            return [
                "Schedule response within 24 hours",
            ]
        return ["Routine handling"]

    @staticmethod
    def _empty_summary(
        entity_id: str, summary_type: str, now: datetime,
    ) -> AISummaryResponse:
        """Return an empty summary for missing entities."""
        return AISummaryResponse(
            metadata=PredictionMetadata(generated_at=now),
            summary_type=summary_type,
            entity_id=entity_id,
            overall_assessment="Entity not found in system.",
            key_observations=[],
            potential_concerns=["Entity not found"],
            confidence_level="low",
            recommended_next_actions=["Verify entity ID"],
            sections=[],
        )