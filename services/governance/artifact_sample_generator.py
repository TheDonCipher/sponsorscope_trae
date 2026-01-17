"""
Shared Artifact Sample Validation System for SponsorScope.ai
Generates and validates screenshot samples for compliance testing
"""

import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from PIL import Image, ImageDraw, ImageFont
import io

@dataclass
class ArtifactSample:
    """Represents a screenshot artifact sample for validation"""
    sample_id: str
    scenario: str
    platform: str
    handle: str
    warning_type: str
    epistemic_state: str
    data_completeness: str
    evidence_count: int
    timestamp: str
    methodology_version: str
    expected_elements: List[str]
    validation_status: str = "pending"
    confidence_score: float = 0.0

class ArtifactSampleGenerator:
    """Generates screenshot samples for UX compliance validation"""
    
    def __init__(self, output_dir: str = "docs/audits/samples"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_sample_scenarios(self) -> List[ArtifactSample]:
        """Generate comprehensive sample scenarios for validation"""
        return [
            ArtifactSample(
                sample_id="sample_001_private_instagram",
                scenario="Private Instagram account with login wall",
                platform="instagram",
                handle="@test_private_123",
                warning_type="ACCESS_DENIED",
                epistemic_state="LIMITED",
                data_completeness="partial_no_comments",
                evidence_count=4,
                timestamp=datetime.now().isoformat(),
                methodology_version="v2.4",
                expected_elements=[
                    "SponsorScope.ai",
                    "ACCESS DENIED",
                    "This account is private",
                    "4 public evidence items",
                    "v2.4",
                    "ESTIMATED",
                    "Confidence Interval"
                ]
            ),
            
            ArtifactSample(
                sample_id="sample_002_deleted_account",
                scenario="Deleted/non-existent account",
                platform="instagram",
                handle="@deleted_user_test",
                warning_type="SYSTEM_WARNING",
                epistemic_state="INSUFFICIENT",
                data_completeness="unavailable",
                evidence_count=0,
                timestamp=datetime.now().isoformat(),
                methodology_version="v2.4",
                expected_elements=[
                    "SponsorScope.ai",
                    "SYSTEM WARNING",
                    "Account unavailable",
                    "0 evidence items",
                    "v2.4",
                    "Insufficient data",
                    "Cannot analyze"
                ]
            ),
            
            ArtifactSample(
                sample_id="sample_003_rate_limited",
                scenario="Rate limited account blocking comments",
                platform="instagram",
                handle="@rate_limited_test",
                warning_type="SIGNAL_BLOCKED",
                epistemic_state="LIMITED",
                data_completeness="partial_no_comments",
                evidence_count=3,
                timestamp=datetime.now().isoformat(),
                methodology_version="v2.4",
                expected_elements=[
                    "SponsorScope.ai",
                    "SIGNAL BLOCKED",
                    "Rate limiting active",
                    "3 evidence items",
                    "v2.4",
                    "Comments unavailable",
                    "Limited analysis"
                ]
            ),
            
            ArtifactSample(
                sample_id="sample_004_archival_data",
                scenario="Archival fallback data usage",
                platform="instagram",
                handle="@archival_data_test",
                warning_type="SYSTEM_WARNING",
                epistemic_state="ROBUST",
                data_completeness="archival",
                evidence_count=7,
                timestamp=datetime.now().isoformat(),
                methodology_version="v2.4",
                expected_elements=[
                    "SponsorScope.ai",
                    "SYSTEM WARNING",
                    "Using archival data",
                    "7 archival evidence items",
                    "v2.4",
                    "Fallback analysis",
                    "Historical patterns"
                ]
            ),
            
            ArtifactSample(
                sample_id="sample_005_sparse_data",
                scenario="Insufficient sample size for analysis",
                platform="tiktok",
                handle="@sparse_data_test",
                warning_type="LOW_SAMPLE_SIZE",
                epistemic_state="LIMITED",
                data_completeness="sparse",
                evidence_count=2,
                timestamp=datetime.now().isoformat(),
                methodology_version="v2.4",
                expected_elements=[
                    "SponsorScope.ai",
                    "LOW SAMPLE SIZE",
                    "Insufficient data",
                    "2 evidence items",
                    "v2.4",
                    "±15% margin of error",
                    "Statistical confidence low"
                ]
            ),
            
            ArtifactSample(
                sample_id="sample_006_comments_disabled",
                scenario="Creator disabled comments on posts",
                platform="instagram",
                handle="@comments_disabled_test",
                warning_type="SIGNAL_BLOCKED",
                epistemic_state="LIMITED",
                data_completeness="partial_no_comments",
                evidence_count=5,
                timestamp=datetime.now().isoformat(),
                methodology_version="v2.4",
                expected_elements=[
                    "SponsorScope.ai",
                    "SIGNAL BLOCKED",
                    "Comments disabled",
                    "5 evidence items",
                    "v2.4",
                    "Linguistic analysis unavailable",
                    "Engagement quality limited"
                ]
            )
        ]
    
    def create_screenshot_mock(self, sample: ArtifactSample) -> bytes:
        """Create a mock screenshot image with compliance elements"""
        # Create base image (1920x1080 for desktop screenshot)
        img = Image.new('RGB', (1920, 1080), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a system font, fallback to default if not available
        try:
            font_large = ImageFont.truetype("arial.ttf", 48)
            font_medium = ImageFont.truetype("arial.ttf", 32)
            font_small = ImageFont.truetype("arial.ttf", 24)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw header with platform branding
        draw.rectangle([0, 0, 1920, 120], fill='#1a1a1a')
        draw.text((50, 30), "SponsorScope.ai", fill='#ffffff', font=font_large)
        draw.text((50, 85), f"v{sample.methodology_version} • {sample.timestamp[:10]}", 
                 fill='#888888', font=font_small)
        
        # Draw warning banner based on type
        warning_colors = {
            'ACCESS_DENIED': ('#374151', '#f3f4f6'),
            'SYSTEM_WARNING': ('#4338ca', '#e0e7ff'),
            'SIGNAL_BLOCKED': ('#d97706', '#fef3c7'),
            'LOW_SAMPLE_SIZE': ('#1d4ed8', '#dbeafe')
        }
        
        bg_color, text_color = warning_colors.get(sample.warning_type, ('#374151', '#f3f4f6'))
        draw.rectangle([0, 120, 1920, 200], fill=bg_color)
        
        warning_text = sample.warning_type.replace('_', ' ')
        draw.text((50, 135), warning_text, fill=text_color, font=font_medium)
        
        # Draw main content area
        content_y = 250
        
        # Handle and platform info
        draw.text((50, content_y), f"Platform: {sample.platform}", fill='#333333', font=font_medium)
        draw.text((50, content_y + 50), f"Handle: {sample.handle}", fill='#333333', font=font_medium)
        draw.text((50, content_y + 100), f"Scenario: {sample.scenario}", fill='#666666', font=font_small)
        
        # Evidence count and epistemic state
        draw.text((50, content_y + 150), f"Evidence Count: {sample.evidence_count}", 
                 fill='#059669', font=font_medium)
        draw.text((50, content_y + 200), f"Epistemic State: {sample.epistemic_state}", 
                 fill='#d97706', font=font_medium)
        
        # Probabilistic framing section
        draw.text((50, content_y + 280), "ESTIMATED AUTHENTICITY SCORE", 
                 fill='#1f2937', font=font_medium)
        draw.text((50, content_y + 330), "Confidence Interval: 65% ±15%", 
                 fill='#6b7280', font=font_small)
        draw.text((50, content_y + 370), "Signal Strength: Moderate", 
                 fill='#6b7280', font=font_small)
        draw.text((50, content_y + 410), "Uncertainty: High", 
                 fill='#6b7280', font=font_small)
        
        # Watermark at bottom
        draw.rectangle([0, 980, 1920, 1080], fill='#f9fafb')
        watermark_text = f"SponsorScope.ai • {sample.timestamp[:10]} • v{sample.methodology_version} • ESTIMATED ANALYSIS"
        draw.text((50, 1020), watermark_text, fill='#9ca3af', font=font_small)
        
        # Add border
        draw.rectangle([0, 0, 1919, 1079], outline='#e5e7eb', width=2)
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer.getvalue()
    
    def validate_artifact_sample(self, sample: ArtifactSample, screenshot_path: Path) -> Dict:
        """Validate an artifact sample against expected criteria"""
        validation_result = {
            "sample_id": sample.sample_id,
            "validation_status": "pending",
            "confidence_score": 0.0,
            "passed_checks": [],
            "failed_checks": [],
            "warnings": []
        }
        
        # Check if screenshot file exists
        if not screenshot_path.exists():
            validation_result["failed_checks"].append("Screenshot file not found")
            validation_result["validation_status"] = "failed"
            return validation_result
        
        # Validate filename format
        expected_filename = f"{sample.sample_id}_{sample.platform}_{sample.data_completeness}_{sample.epistemic_state}.png"
        if screenshot_path.name != expected_filename:
            validation_result["warnings"].append(f"Filename mismatch: expected {expected_filename}")
        
        # Validate metadata (simulated - in practice would use OCR)
        passed_checks = []
        failed_checks = []
        
        # Check for expected elements (simulated)
        for element in sample.expected_elements:
            # In practice, would use OCR to detect elements in image
            # For simulation, we'll assume some elements are present
            if "SponsorScope.ai" in element or sample.platform in element:
                passed_checks.append(f"Found: {element}")
            else:
                failed_checks.append(f"Missing: {element}")
        
        # Calculate confidence score
        total_checks = len(sample.expected_elements)
        passed_count = len(passed_checks)
        confidence_score = (passed_count / total_checks) * 100 if total_checks > 0 else 0
        
        validation_result["passed_checks"] = passed_checks
        validation_result["failed_checks"] = failed_checks
        validation_result["confidence_score"] = confidence_score
        
        # Determine overall status
        if confidence_score >= 80:
            validation_result["validation_status"] = "passed"
        elif confidence_score >= 60:
            validation_result["validation_status"] = "partial"
        else:
            validation_result["validation_status"] = "failed"
        
        return validation_result
    
    def generate_all_samples(self) -> List[Dict]:
        """Generate all artifact samples and validate them"""
        samples = self.generate_sample_scenarios()
        results = []
        
        print(f"Generating {len(samples)} artifact samples...")
        
        for sample in samples:
            # Create screenshot mock
            screenshot_data = self.create_screenshot_mock(sample)
            
            # Save screenshot
            screenshot_path = self.output_dir / f"{sample.sample_id}_{sample.platform}_{sample.data_completeness}_{sample.epistemic_state}.png"
            with open(screenshot_path, 'wb') as f:
                f.write(screenshot_data)
            
            # Validate sample
            validation_result = self.validate_artifact_sample(sample, screenshot_path)
            
            # Combine sample data with validation results
            sample_dict = asdict(sample)
            sample_dict.update(validation_result)
            sample_dict["screenshot_path"] = str(screenshot_path)
            
            results.append(sample_dict)
            
            status = "✅ PASS" if validation_result["validation_status"] == "passed" else "⚠️ PARTIAL" if validation_result["validation_status"] == "partial" else "❌ FAIL"
            print(f"  {sample.sample_id}: {status} ({validation_result['confidence_score']:.1f}% confidence)")
        
        return results
    
    def generate_validation_report(self, results: List[Dict]) -> Dict:
        """Generate comprehensive validation report"""
        total_samples = len(results)
        passed_samples = sum(1 for r in results if r["validation_status"] == "passed")
        partial_samples = sum(1 for r in results if r["validation_status"] == "partial")
        failed_samples = sum(1 for r in results if r["validation_status"] == "failed")
        
        avg_confidence = sum(r["confidence_score"] for r in results) / total_samples if total_samples > 0 else 0
        
        # Analyze failure patterns
        failure_patterns = {}
        for result in results:
            for failure in result.get("failed_checks", []):
                failure_type = failure.split(":")[0]
                failure_patterns[failure_type] = failure_patterns.get(failure_type, 0) + 1
        
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "framework_version": "1.0.0",
                "total_samples": total_samples,
                "passed_samples": passed_samples,
                "partial_samples": partial_samples,
                "failed_samples": failed_samples,
                "average_confidence": f"{avg_confidence:.1f}%"
            },
            "validation_summary": {
                "watermark_detection": avg_confidence >= 70,
                "probabilistic_framing": avg_confidence >= 60,
                "warning_display": passed_samples >= 4,
                "metadata_compliance": passed_samples >= 5
            },
            "failure_analysis": failure_patterns,
            "detailed_results": results,
            "recommendations": self._generate_recommendations(results, avg_confidence)
        }
        
        return report
    
    def _generate_recommendations(self, results: List[Dict], avg_confidence: float) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if avg_confidence < 70:
            recommendations.append("Improve watermark visibility and OCR detection accuracy")
        
        if avg_confidence < 60:
            recommendations.append("Enhance probabilistic language prominence in screenshots")
        
        failed_count = sum(1 for r in results if r["validation_status"] == "failed")
        if failed_count > 2:
            recommendations.append("Review screenshot generation pipeline for consistency issues")
        
        # Check for common failure patterns
        failure_patterns = {}
        for result in results:
            for failure in result.get("failed_checks", []):
                failure_type = failure.split(":")[0]
                failure_patterns[failure_type] = failure_patterns.get(failure_type, 0) + 1
        
        if failure_patterns.get("Missing", 0) > 10:
            recommendations.append("Implement stronger element detection and positioning")
        
        if not recommendations:
            recommendations.append("Validation system performing well - consider expanding test coverage")
        
        return recommendations

def main():
    """Main function to generate and validate artifact samples"""
    generator = ArtifactSampleGenerator()
    
    print("🎨 Generating SponsorScope.ai Artifact Samples")
    print("=" * 60)
    
    # Generate all samples
    results = generator.generate_all_samples()
    
    # Generate validation report
    report = generator.generate_validation_report(results)
    
    # Save report
    report_path = generator.output_dir / "validation_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Save sample manifest
    manifest_path = generator.output_dir / "sample_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"📊 Validation Report Generated: {report_path}")
    print(f"📋 Sample Manifest: {manifest_path}")
    print(f"🎯 Average Confidence: {report['report_metadata']['average_confidence']}")
    print(f"✅ Passed: {report['report_metadata']['passed_samples']}")
    print(f"⚠️  Partial: {report['report_metadata']['partial_samples']}")
    print(f"❌ Failed: {report['report_metadata']['failed_samples']}")
    
    return report

if __name__ == "__main__":
    main()