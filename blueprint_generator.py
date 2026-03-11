"""
Blueprint Generator for YouTube Content Strategy.
Creates actionable content blueprints, strategy recommendations, and growth roadmaps.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class ContentBlueprintGenerator:
    """Generates strategic content blueprints from analysis data."""
    
    @staticmethod
    def generate_video_strategy(analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate recommended video strategy based on analysis.
        
        Args:
            analysis: Comprehensive analysis results
            
        Returns:
            Dictionary with video strategy recommendations
        """
        logger.info("Generating video strategy...")
        
        content_strategy = analysis.get("content_strategy", {})
        
        # Extract length recommendation
        length_analysis = content_strategy.get("video_lengths", {})
        distribution = length_analysis.get("distribution", {})
        
        # Determine optimal length
        if distribution.get("medium_form_10_20min", {}).get("percentage", 0) > 40:
            optimal_length = "10-20 minutes"
            reasoning = "Medium-form content dominates this niche"
        elif distribution.get("short_form_10min_or_less", {}).get("percentage", 0) > 40:
            optimal_length = "5-10 minutes"
            reasoning = "Short-form content is most prevalent"
        else:
            optimal_length = "15-25 minutes"
            reasoning = "Long-form content attracts more engagement in this niche"
        
        # Extract upload frequency
        upload_patterns = content_strategy.get("upload_patterns", {})
        frequency = upload_patterns.get("average_upload_frequency_per_week", 1)
        
        if frequency >= 3:
            upload_freq = "3-4 times per week"
        elif frequency >= 1.5:
            upload_freq = "2 times per week"
        else:
            upload_freq = "1-2 times per week"
        
        # Best upload times
        upload_days = upload_patterns.get("most_common_upload_days", [])
        peak_hours = upload_patterns.get("peak_upload_hours", [])
        
        best_day = upload_days[0][0] if upload_days else "Tuesday"
        best_hour = peak_hours[0][0] if peak_hours else 14  # 2 PM
        
        # Title patterns
        title_analysis = content_strategy.get("title_analysis", {})
        title_patterns = title_analysis.get("patterns", {})
        
        recommended_title_style = "Mixed format"
        if title_patterns.get("question_mark_titles", {}).get("percentage", 0) > 30:
            recommended_title_style = "Question-based titles work well"
        elif title_patterns.get("number_titles", {}).get("percentage", 0) > 30:
            recommended_title_style = "Number-based titles (Top 10, 5 Ways, etc.)"
        
        return {
            "optimal_video_length": optimal_length,
            "length_reasoning": reasoning,
            "recommended_upload_frequency": upload_freq,
            "best_upload_day": best_day,
            "best_upload_time": f"{best_hour}:00 (2-3 PM range)",
            "recommended_title_style": recommended_title_style,
            "title_recommendations": [
                "Include numbers or lists (Top 5, 10 Tips, etc.)",
                "Ask questions to spark curiosity",
                "Include brackets for clarification [Tutorial], [Vlog], etc.",
                "Keep between 50-70 characters for optimal CTR",
                "Put keywords near the beginning"
            ],
            "thumbnail_style": {
                "recommendation": "High contrast colors with clear focal point",
                "tips": [
                    "Use bright colors that stand out in YouTube feeds",
                    "Include faces with strong emotions when relevant",
                    "Add text overlays (max 5-7 words)",
                    "Keep text size large and readable at 168x94px",
                    "Use consistent branding across thumbnails"
                ]
            },
            "description_best_practices": [
                "Include timestamps for longer videos",
                "Add clear CTAs (Subscribe, Like, Comment, etc.)",
                "Include relevant links in first 200 characters",
                "Use keywords naturally in first 2-3 sentences",
                "Add hashtags at the end (3-5 maximum)"
            ]
        }
    
    @staticmethod
    def generate_content_ideas(analysis: Dict[str, Any], niche: str) -> List[Dict[str, Any]]:
        """
        Generate top 5 content ideas based on analysis gaps and trends.
        
        Args:
            analysis: Comprehensive analysis results
            niche: Niche category
            
        Returns:
            List of top 5 content ideas with detailed recommendations
        """
        logger.info("Generating content ideas...")
        
        gaps = analysis.get("competition", {}).get("content_gaps", {})
        trending = analysis.get("growth", {}).get("trending_topics", {})
        engagement = analysis.get("engagement", {}).get("engagement_analysis", {})
        
        ideas = []
        
        # Idea 1: Trending topic with unique angle
        trending_topics = trending.get("trending_topics", [])
        if trending_topics:
            top_topic = trending_topics[0].get("topic", "trending topic")
            ideas.append({
                "rank": 1,
                "title": f"The Complete Guide to {top_topic.title()} in {niche}",
                "type": "Tutorial/Educational",
                "rationale": f"'{top_topic}' is trending with {trending_topics[0].get('mentions', 0)} mentions in recent videos. Create the definitive guide.",
                "recommended_length": "15-20 minutes",
                "target_audience": "Beginners to intermediate",
                "thumbnail_guidance": "Show before/after or step-by-step preview",
                "title_options": [
                    f"How to Master {top_topic} - Beginner's Guide",
                    f"Everything You Need to Know About {top_topic}",
                    f"The {top_topic} Strategy That Works"
                ],
                "hook_strategy": "Start with a surprising stat or common mistake",
                "estimated_views": "500-2000 views",
                "difficulty": "Medium"
            })
        
        # Idea 2: Beginner-focused content
        ideas.append({
            "rank": 2,
            "title": f"{niche} for Beginners - Start Here",
            "type": "Educational/Beginner Guide",
            "rationale": "Beginner content evergreen and consistently gets views. Low competition opportunity.",
            "recommended_length": "12-15 minutes",
            "target_audience": "Complete beginners",
            "thumbnail_guidance": "Include 'START HERE' text, welcoming expression",
            "title_options": [
                f"{niche} for Beginners: Everything You Need",
                f"New to {niche}? Watch This First",
                f"Complete Beginner's Roadmap to {niche}"
            ],
            "hook_strategy": "Show the end result first, promise to get them there",
            "estimated_views": "1000-5000 views",
            "difficulty": "Easy"
        })
        
        # Idea 3: Common mistakes/problems
        ideas.append({
            "rank": 3,
            "title": f"7 Biggest Mistakes in {niche} (And How to Fix Them)",
            "type": "Problem-solving",
            "rationale": "Mistake/problem-focused content has high engagement. Solves real pain points.",
            "recommended_length": "10-15 minutes",
            "target_audience": "Practitioners, intermediate level",
            "thumbnail_guidance": "Show frustrated face or red X marks",
            "title_options": [
                f"Stop Making These {niche} Mistakes",
                f"Common {niche} Problems and Solutions",
                f"Why You're Failing at {niche}"
            ],
            "hook_strategy": "Start with 'You're probably doing this wrong...'",
            "estimated_views": "800-3000 views",
            "difficulty": "Medium"
        })
        
        # Idea 4: Advanced/Deep dive
        ideas.append({
            "rank": 4,
            "title": f"Advanced {niche} Tactics (Pro Level)",
            "type": "Advanced Tutorial",
            "rationale": "Advanced content has smaller audience but higher engagement and better for building authority.",
            "recommended_length": "20-30 minutes",
            "target_audience": "Advanced practitioners, experts",
            "thumbnail_guidance": "Include 'PRO' badge or advanced indicator",
            "title_options": [
                f"Advanced {niche} Techniques for 2025",
                f"Pro Tips That Most People Don't Know",
                f"Unlock Advanced {niche} Strategies"
            ],
            "hook_strategy": "Start with surprising advanced technique",
            "estimated_views": "300-1500 views",
            "difficulty": "Hard"
        })
        
        # Idea 5: Comparison or case study
        ideas.append({
            "rank": 5,
            "title": f"Comparing Different {niche} Methods: Which Works Best?",
            "type": "Comparison/Analysis",
            "rationale": "Comparison videos drive engagement as viewers debate approaches. Good for comment CTR.",
            "recommended_length": "15-20 minutes",
            "target_audience": "Decision-makers, all levels",
            "thumbnail_guidance": "Show multiple options or A vs B layout",
            "title_options": [
                f"Method A vs Method B in {niche} - Full Comparison",
                f"Best {niche} Approaches Ranked and Tested",
                f"I Tested Every {niche} Technique"
            ],
            "hook_strategy": "Reveal surprising winner upfront",
            "estimated_views": "600-2500 views",
            "difficulty": "Medium"
        })
        
        return ideas
    
    @staticmethod
    def generate_what_works(analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Build 'what works' from actual correlation data + data-driven insights,
        then supplement with universal best practices only where data is thin.
        """
        logger.info("Extracting what works...")

        data_driven = analysis.get("data_driven_insights", {}).get("what_works", {})
        correlations = analysis.get("correlations", {})

        engagement_drivers = list(data_driven.get("engagement_drivers", []))
        title_strategies = list(data_driven.get("title_strategies", []))
        format_insights = list(data_driven.get("format_insights", []))

        # Add correlation-based insights
        length_corr = correlations.get("length_vs_performance", {})
        best_length = length_corr.get("best_performing_length", "")
        if best_length and best_length != "unknown":
            bracket_data = length_corr.get("by_bracket", {}).get(best_length, {})
            if bracket_data.get("count", 0) >= 2:
                format_insights.append(
                    f"Best performing format: {best_length} — median {bracket_data.get('median_views', 0):,} views, "
                    f"{bracket_data.get('avg_engagement', 0):.2f}% engagement ({bracket_data['count']} videos)"
                )

        title_corr = correlations.get("title_patterns_vs_performance", {})
        for p in title_corr.get("positive_patterns", [])[:3]:
            pattern = p["pattern"].replace("has_", "").replace("_", " ")
            title_strategies.append(
                f"Titles with {pattern}: +{p['view_lift_percent']:.0f}% more views "
                f"({p['median_views_with']:,} vs {p['median_views_without']:,} median)"
            )

        day_corr = correlations.get("upload_day_vs_performance", {})
        best_day = day_corr.get("best_day", "")
        if best_day:
            day_data = day_corr.get("by_day", {}).get(best_day, {})
            if day_data.get("count", 0) >= 2:
                engagement_drivers.append(
                    f"Best upload day: {best_day} — {day_data.get('median_views', 0):,} median views "
                    f"({day_data['count']} videos)"
                )

        # Add universal best practices only if we have fewer than 3 data points
        if len(engagement_drivers) < 3:
            engagement_drivers.extend([
                "Strong hook in first 10 seconds that addresses a specific viewer pain point",
                "Consistent upload schedule to train the algorithm and build viewer habit",
            ])

        return {
            "engagement_drivers": engagement_drivers,
            "title_strategies": title_strategies,
            "format_insights": format_insights,
            "best_practices": [
                "Engage in comments within first 24h (signals active channel to algorithm)",
                "Create playlists to boost session watch time",
                "Use chapter markers in descriptions for longer videos",
                "Include clear CTA at natural moments, not just at the end",
            ],
        }
    
    @staticmethod
    def generate_what_doesnt_work(analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Build 'what doesn't work' from actual data — comparing bottom-performing
        videos against the top, supplemented with universal pitfalls.
        """
        logger.info("Identifying what doesn't work...")

        data_driven = analysis.get("data_driven_insights", {}).get("what_doesnt_work", {})
        correlations = analysis.get("correlations", {})

        content_warnings = list(data_driven.get("content_warnings", []))
        title_warnings = list(data_driven.get("title_warnings", []))
        format_warnings = list(data_driven.get("format_warnings", []))

        # Add negative title patterns from correlations
        title_corr = correlations.get("title_patterns_vs_performance", {})
        for p in title_corr.get("negative_patterns", [])[:3]:
            pattern = p["pattern"].replace("has_", "").replace("_", " ")
            title_warnings.append(
                f"Titles with {pattern}: {p['view_lift_percent']:.0f}% fewer views "
                f"({p['median_views_with']:,} vs {p['median_views_without']:,} median)"
            )

        # Universal pitfalls if data-driven list is thin
        if len(content_warnings) < 2:
            content_warnings.extend([
                "Inconsistent upload schedule loses algorithm momentum",
                "Ignoring audience comments misses feedback loops",
            ])
        if len(title_warnings) < 2:
            title_warnings.extend([
                "Clickbait titles that don't deliver cause high bounce rates",
                "Vague titles that don't promise a specific benefit",
            ])

        return {
            "content_warnings": content_warnings,
            "title_warnings": title_warnings,
            "format_warnings": format_warnings,
        }
    
    @staticmethod
    def generate_competitive_positioning(analysis: Dict[str, Any], niche: str) -> Dict[str, Any]:
        """
        Create competitive positioning strategy.
        
        Args:
            analysis: Comprehensive analysis results
            niche: Niche category
            
        Returns:
            Competitive positioning report
        """
        logger.info("Creating competitive positioning report...")
        
        competition = analysis.get("competition", {})
        top_channels = competition.get("competitive_landscape", {}).get("top_channels", [])
        saturation = competition.get("competitive_landscape", {}).get("market_saturation", "Medium")
        gaps = competition.get("content_gaps", {})
        
        return {
            "market_saturation_level": saturation,
            "saturation_interpretation": {
                "High": "Niche is competitive but proven demand. Need strong differentiation.",
                "Medium": "Moderate competition. Opportunity for new entrants with good positioning.",
                "Low": "Less competition but potentially lower demand. Test content carefully."
            }.get(saturation, "Unknown"),
            "differentiation_strategies": [
                f"Focus on under-explored angle in {niche}",
                "Build personal brand with consistent personality",
                "Create highest quality content (production values) in niche",
                "Develop unique teaching methodology or framework",
                "Serve underserved segment (advanced, beginners, specific demographic)",
                "Collaborate with complementary creators",
                "Build community (Discord, email list) around content"
            ],
            "underexplored_subtopics": gaps.get("low_frequency_topics", [])[:5],
            "content_opportunities": [
                "Address pain points in top creators' comments",
                "Create detailed deep-dives on single topics (while others skim)",
                "Develop response/reaction content to trending videos",
                "Create 'ultimate guide' or 'definitive' version of existing content",
                "Target long-tail keywords less creators are using"
            ],
            "partnership_opportunities": [
                "Collaborate with top creators for cross-promotion",
                "Partner with complementary niche creators",
                "Reach out to brands relevant to your audience",
                "Create affiliate relationships with useful tools",
                "Partner with educational platforms for knowledge"
            ],
            "unique_positioning_angle": f"To succeed in {niche}, develop a unique angle (teaching style, personality, niche segment) that sets you apart from top {len(top_channels)} creators"
        }
    
    @staticmethod
    def generate_growth_roadmap(analysis: Dict[str, Any], niche: str) -> Dict[str, Dict[str, List[str]]]:
        """
        Create 3-phase growth roadmap driven by actual analysis data.
        """
        logger.info("Creating growth roadmap...")

        trending_raw = analysis.get("growth", {}).get("trending_topics", {}).get("trending_topics", [])
        trending_names = [t.get("topic", "") for t in trending_raw[:6] if t.get("topic")]

        gaps = analysis.get("competition", {}).get("content_gaps", {})
        low_freq = [t.get("topic", "") for t in gaps.get("low_frequency_topics", [])[:5] if t.get("topic")]
        high_sat = [t.get("topic", "") for t in gaps.get("high_saturation_topics", [])[:5] if t.get("topic")]

        engagement = analysis.get("engagement", {}).get("engagement_analysis", {})
        median_views = int(engagement.get("median_views", 0))
        avg_views = int(engagement.get("average_views_per_video", 0))
        benchmarks = engagement.get("engagement_benchmarks", {})
        avg_like_ratio = benchmarks.get("average_like_ratio_percent", 0)
        avg_engagement = benchmarks.get("average_engagement_rate_percent", 0)

        competition = analysis.get("competition", {}).get("competitive_landscape", {})
        saturation = competition.get("market_saturation", "Medium")
        top_channels = competition.get("top_channels", [])
        top_channel_names = [c.get("name", "") for c in top_channels[:5] if isinstance(c, dict)]

        content_strategy = analysis.get("content_strategy", {})
        upload_patterns = content_strategy.get("upload_patterns", {})
        upload_freq = upload_patterns.get("average_upload_frequency_per_week", 1)
        best_days = upload_patterns.get("most_common_upload_days", [])
        best_day_name = best_days[0][0] if best_days else "weekdays"

        length_dist = content_strategy.get("video_lengths", {}).get("distribution", {})
        short_pct = length_dist.get("short_form_10min_or_less", {}).get("percentage", 0)
        medium_pct = length_dist.get("medium_form_10_20min", {}).get("percentage", 0)
        long_pct = length_dist.get("long_form_20min_plus", {}).get("percentage", 0)
        if long_pct >= medium_pct and long_pct >= short_pct:
            dominant_format = "long-form (20+ min)"
        elif medium_pct >= short_pct:
            dominant_format = "medium-form (10-20 min)"
        else:
            dominant_format = "short-form (<10 min)"

        view_dist = engagement.get("view_distribution", {})
        under_10k = view_dist.get("0_1k", 0) + view_dist.get("1k_10k", 0)
        total_vids = engagement.get("total_videos", 1) or 1
        pct_under_10k = round((under_10k / total_vids) * 100)

        # Calibrate success targets to the niche's actual numbers
        phase1_view_target = max(200, median_views // 10)
        phase2_view_target = max(1000, median_views // 3)

        saturation_advice = {
            "High": f"This niche is highly saturated ({len(top_channels)} competing channels in the sample). Differentiation is critical — find a sub-niche or unique angle rather than competing head-on with {', '.join(top_channel_names[:3]) or 'top creators'}.",
            "Medium": f"Moderate competition ({len(top_channels)} channels). There's room for new creators, especially if you target under-explored angles.",
            "Low": f"Low competition — fewer creators means less proven demand but more opportunity to become the go-to channel."
        }.get(saturation, "")

        phase1_topics = []
        if low_freq:
            phase1_topics.append(f"Under-explored topics to target: {', '.join(low_freq[:3])}")
        if trending_names:
            phase1_topics.append(f"Ride trending momentum: {', '.join(trending_names[:3])}")
        phase1_topics.append(f"Foundational '{niche} for beginners' content (evergreen)")
        phase1_topics.append(f"'Common {niche} mistakes' or 'what I wish I knew' content")
        if high_sat:
            phase1_topics.append(f"Add unique angle to high-demand topics: {', '.join(high_sat[:2])}")

        phase2_topics = []
        if trending_names:
            phase2_topics.append(f"Deep-dive series on trending topics: {', '.join(trending_names[:3])}")
        if low_freq:
            phase2_topics.append(f"Expand into gap topics competitors are ignoring: {', '.join(low_freq[:3])}")
        phase2_topics.append(f"Comparison and 'vs' content (high comment engagement in this niche)")
        phase2_topics.append("Case studies and real-world results to build authority")

        return {
            "niche_context": saturation_advice,
            "phase_1_foundation": {
                "duration": "Months 1-3 (30-50 videos)",
                "goal": f"Establish presence in {niche} and find your audience",
                "focus_areas": [
                    f"Upload {max(1, round(upload_freq))}x/week — matching the niche cadence (best day: {best_day_name})",
                    f"Focus on {dominant_format} videos since that's what performs in this niche ({long_pct:.0f}% long / {medium_pct:.0f}% medium / {short_pct:.0f}% short)",
                    f"Target a like ratio above {avg_like_ratio:.1f}% (the niche average) by asking for engagement in your hooks",
                    "Optimize every video for search: keywords in title + description + tags",
                    "Engage heavily in comments in the first 24h after each upload",
                ],
                "key_topics": phase1_topics,
                "metrics_to_track": [
                    "Upload consistency (hit 100% of your schedule)",
                    f"Average views per video (aim for {phase1_view_target:,}+ — {pct_under_10k}% of videos in this niche get under 10K views so this is realistic)",
                    "Audience retention above 40%",
                    "Click-through rate above 5%",
                    f"Engagement rate above {avg_engagement:.1f}% (niche benchmark)",
                ],
                "success_criteria": f"1,000 subscribers, averaging {phase1_view_target:,}+ views per video"
            },
            "phase_2_scaling": {
                "duration": "Months 3-6 (additional 30-50 videos)",
                "goal": "Double down on what works, grow faster",
                "focus_areas": [
                    "Analyze your top 5 videos and create follow-up series on those topics",
                    f"Study what {', '.join(top_channel_names[:3]) or 'top creators'} do well — adapt, don't copy",
                    "Increase production quality (better audio, graphics, editing)",
                    f"Collaborate with other {niche} creators for cross-promotion",
                    "Create playlists to boost session watch time",
                ],
                "key_topics": phase2_topics,
                "metrics_to_track": [
                    f"Average views per video (aim for {phase2_view_target:,}+)",
                    "Subscriber growth rate acceleration",
                    "Watch time toward 4,000 hours/year (monetization threshold)",
                    "Returning viewer percentage",
                ],
                "success_criteria": f"10,000 subscribers, averaging {phase2_view_target:,}+ views per video"
            },
            "phase_3_monetization": {
                "duration": "Months 6-12 (ongoing content)",
                "goal": "Monetize your audience and build sustainable revenue",
                "focus_areas": [
                    "Apply for YouTube Partner Program once you hit 1K subs + 4K watch hours",
                    f"Pursue sponsorships — brands in the {niche} space pay for targeted audiences",
                    "Build an email list from your audience (lead magnet in descriptions)",
                    f"Create a digital product (course, templates, guides) based on your most-viewed {niche} topics",
                    "Launch a community (Discord/Patreon) for your most engaged viewers",
                ],
                "monetization_strategies": [
                    "YouTube ad revenue (baseline income)",
                    f"Sponsored content from {niche}-adjacent brands",
                    "Affiliate links for tools and products you actually use",
                    "Digital products (courses or guides based on your top-performing content)",
                    "Paid community or membership tier",
                ],
                "key_topics": [
                    "Premium deep-dives on topics your audience asks for most",
                    f"Interview other {niche} creators or experts",
                    "Behind-the-scenes and personal journey content (builds loyalty)",
                    "'State of the industry' or trend analysis content",
                ],
                "metrics_to_track": [
                    "Monthly ad revenue (track CPM by video type)",
                    "Sponsorship deal flow and rates",
                    "Email list size and open rates",
                    "Product/course revenue",
                    "Community member count and retention",
                ],
                "success_criteria": "50,000+ subscribers, diversified revenue, $500+/month"
            }
        }


class BlueprintOrchestrator:
    """Orchestrates blueprint generation from analysis."""
    
    def __init__(self):
        """Initialize blueprint generator."""
        self.generator = ContentBlueprintGenerator()
    
    def generate_complete_blueprint(self, analysis: Dict[str, Any], niche: str) -> Dict[str, Any]:
        """
        Generate complete blueprint.
        
        Args:
            analysis: Comprehensive analysis results
            niche: Niche category
            
        Returns:
            Complete blueprint with all sections
        """
        logger.info(f"Generating complete blueprint for niche: {niche}")
        
        blueprint = {
            "niche": niche,
            "generated_at": datetime.utcnow().isoformat(),
            "video_strategy": self.generator.generate_video_strategy(analysis),
            "content_ideas": self.generator.generate_content_ideas(analysis, niche),
            "what_works": self.generator.generate_what_works(analysis),
            "what_doesnt_work": self.generator.generate_what_doesnt_work(analysis),
            "competitive_positioning": self.generator.generate_competitive_positioning(analysis, niche),
            "growth_roadmap": self.generator.generate_growth_roadmap(analysis, niche)
        }
        
        logger.info("Blueprint generation complete")
        return blueprint
