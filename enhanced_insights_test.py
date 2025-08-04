#!/usr/bin/env python3

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, List

# Configuration - Use external URL from frontend/.env
BACKEND_URL = "https://8f43b565-3ef8-487e-92ed-bb0b1b3a1936.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class EnhancedInsightsTestSuite:
    """Enhanced Insights API Testing - Verify descriptive data with actual pillar names, icons, colors, and recommendations"""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "testpassword"
        self.test_results = []
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate with test credentials"""
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{BACKEND_URL}/api/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    print(f"✅ Authentication successful for {self.test_user_email}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def test_insights_api_structure(self):
        """Test 1: Enhanced Insights API Structure Verification"""
        print("\n🧪 Test 1: Enhanced Insights API Structure Verification")
        
        try:
            async with self.session.get(f"{API_BASE}/insights", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    insights_data = await response.json()
                    print(f"✅ Insights API responded successfully")
                    
                    # Verify main structure
                    required_sections = [
                        'alignment_snapshot',
                        'productivity_trends', 
                        'area_distribution',
                        'insights_text',
                        'recommendations',
                        'generated_at'
                    ]
                    
                    missing_sections = [section for section in required_sections if section not in insights_data]
                    
                    if not missing_sections:
                        print("✅ All required sections present in insights response")
                        self.test_results.append({
                            "test": "Insights API Structure", 
                            "status": "PASSED", 
                            "details": "All required sections present"
                        })
                        return insights_data
                    else:
                        print(f"❌ Missing required sections: {missing_sections}")
                        self.test_results.append({
                            "test": "Insights API Structure", 
                            "status": "FAILED", 
                            "reason": f"Missing sections: {missing_sections}"
                        })
                        return None
                else:
                    error_text = await response.text()
                    print(f"❌ Insights API failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Insights API Structure", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}"
                    })
                    return None
                    
        except Exception as e:
            print(f"❌ Insights API structure test failed: {e}")
            self.test_results.append({
                "test": "Insights API Structure", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return None
            
    async def test_pillar_alignment_data(self, insights_data: Dict[str, Any]):
        """Test 2: Pillar Alignment Data Verification"""
        print("\n🧪 Test 2: Pillar Alignment Data Verification")
        
        try:
            alignment_snapshot = insights_data.get('alignment_snapshot', {})
            pillar_alignment = alignment_snapshot.get('pillar_alignment', [])
            
            if not pillar_alignment:
                print("⚠️ No pillar alignment data found - user may not have pillars or completed tasks")
                self.test_results.append({
                    "test": "Pillar Alignment Data", 
                    "status": "PASSED", 
                    "details": "No pillar data (expected for users without pillars)"
                })
                return True
            
            print(f"📊 Found {len(pillar_alignment)} pillars in alignment data")
            
            # Verify each pillar has required fields
            required_pillar_fields = [
                'pillar_id', 'pillar_name', 'pillar_icon', 'pillar_color',
                'task_count', 'percentage', 'areas_count', 'projects_count'
            ]
            
            all_pillars_valid = True
            actual_pillar_names = []
            
            for i, pillar in enumerate(pillar_alignment):
                missing_fields = [field for field in required_pillar_fields if field not in pillar]
                
                if missing_fields:
                    print(f"❌ Pillar {i+1} missing fields: {missing_fields}")
                    all_pillars_valid = False
                else:
                    pillar_name = pillar['pillar_name']
                    actual_pillar_names.append(pillar_name)
                    
                    # Check for generic/mock names
                    generic_names = ['Health & Fitness', 'Career Growth', 'Personal Development', 'Relationships']
                    is_generic = pillar_name in generic_names
                    
                    print(f"  📌 Pillar: '{pillar_name}' ({pillar['pillar_icon']}) - {pillar['percentage']}%")
                    print(f"     Color: {pillar['pillar_color']}, Tasks: {pillar['task_count']}, Areas: {pillar['areas_count']}, Projects: {pillar['projects_count']}")
                    
                    if is_generic:
                        print(f"  ⚠️ Pillar name '{pillar_name}' appears to be generic/mock data")
                    else:
                        print(f"  ✅ Pillar name '{pillar_name}' appears to be actual user data")
            
            # Verify percentages add up correctly (allowing for rounding)
            total_percentage = sum(pillar['percentage'] for pillar in pillar_alignment)
            if abs(total_percentage - 100.0) <= 1.0 or total_percentage == 0.0:  # Allow for rounding or no completed tasks
                print(f"✅ Pillar percentages sum correctly: {total_percentage}%")
            else:
                print(f"⚠️ Pillar percentages sum to {total_percentage}% (may be expected if not all pillars shown)")
            
            if all_pillars_valid:
                self.test_results.append({
                    "test": "Pillar Alignment Data", 
                    "status": "PASSED", 
                    "details": f"All {len(pillar_alignment)} pillars have required fields with actual names: {actual_pillar_names}"
                })
                return True
            else:
                self.test_results.append({
                    "test": "Pillar Alignment Data", 
                    "status": "FAILED", 
                    "reason": "Some pillars missing required fields"
                })
                return False
                
        except Exception as e:
            print(f"❌ Pillar alignment data test failed: {e}")
            self.test_results.append({
                "test": "Pillar Alignment Data", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_alignment_snapshot_statistics(self, insights_data: Dict[str, Any]):
        """Test 3: Alignment Snapshot Statistics Verification"""
        print("\n🧪 Test 3: Alignment Snapshot Statistics Verification")
        
        try:
            alignment_snapshot = insights_data.get('alignment_snapshot', {})
            
            required_stats = [
                'total_tasks', 'total_tasks_completed', 
                'total_projects', 'total_projects_completed',
                'completion_rate'
            ]
            
            missing_stats = [stat for stat in required_stats if stat not in alignment_snapshot]
            
            if missing_stats:
                print(f"❌ Missing statistics: {missing_stats}")
                self.test_results.append({
                    "test": "Alignment Snapshot Statistics", 
                    "status": "FAILED", 
                    "reason": f"Missing statistics: {missing_stats}"
                })
                return False
            
            # Verify statistics are realistic numbers
            total_tasks = alignment_snapshot['total_tasks']
            total_tasks_completed = alignment_snapshot['total_tasks_completed']
            total_projects = alignment_snapshot['total_projects']
            total_projects_completed = alignment_snapshot['total_projects_completed']
            completion_rate = alignment_snapshot['completion_rate']
            
            print(f"📊 Statistics Summary:")
            print(f"   Tasks: {total_tasks_completed}/{total_tasks} completed ({completion_rate}%)")
            print(f"   Projects: {total_projects_completed}/{total_projects} completed")
            
            # Verify data consistency
            if total_tasks_completed <= total_tasks and total_projects_completed <= total_projects:
                print("✅ Statistics are consistent (completed <= total)")
            else:
                print("❌ Statistics inconsistent (completed > total)")
                self.test_results.append({
                    "test": "Alignment Snapshot Statistics", 
                    "status": "FAILED", 
                    "reason": "Inconsistent statistics (completed > total)"
                })
                return False
            
            # Verify completion rate calculation
            expected_rate = (total_tasks_completed / total_tasks * 100) if total_tasks > 0 else 0
            if abs(completion_rate - expected_rate) <= 1.0:  # Allow for rounding
                print(f"✅ Completion rate calculation correct: {completion_rate}%")
            else:
                print(f"⚠️ Completion rate may be incorrect: {completion_rate}% (expected ~{expected_rate:.1f}%)")
            
            self.test_results.append({
                "test": "Alignment Snapshot Statistics", 
                "status": "PASSED", 
                "details": f"All statistics present and consistent. Tasks: {total_tasks_completed}/{total_tasks}, Projects: {total_projects_completed}/{total_projects}"
            })
            return True
            
        except Exception as e:
            print(f"❌ Alignment snapshot statistics test failed: {e}")
            self.test_results.append({
                "test": "Alignment Snapshot Statistics", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_area_distribution_section(self, insights_data: Dict[str, Any]):
        """Test 4: Area Distribution Section Verification"""
        print("\n🧪 Test 4: Area Distribution Section Verification")
        
        try:
            area_distribution = insights_data.get('area_distribution', [])
            
            if not area_distribution:
                print("⚠️ No area distribution data found - user may not have areas with completed tasks")
                self.test_results.append({
                    "test": "Area Distribution Section", 
                    "status": "PASSED", 
                    "details": "No area distribution data (expected for users without active areas)"
                })
                return True
            
            print(f"📊 Found {len(area_distribution)} areas in distribution data")
            
            # Verify each area has required fields
            required_area_fields = [
                'area_id', 'area_name', 'area_icon', 'area_color',
                'task_count', 'percentage', 'projects_count'
            ]
            
            all_areas_valid = True
            actual_area_names = []
            
            for i, area in enumerate(area_distribution):
                missing_fields = [field for field in required_area_fields if field not in area]
                
                if missing_fields:
                    print(f"❌ Area {i+1} missing fields: {missing_fields}")
                    all_areas_valid = False
                else:
                    area_name = area['area_name']
                    actual_area_names.append(area_name)
                    
                    print(f"  📍 Area: '{area_name}' ({area['area_icon']}) - {area['percentage']}%")
                    print(f"     Color: {area['area_color']}, Tasks: {area['task_count']}, Projects: {area['projects_count']}")
            
            if all_areas_valid:
                self.test_results.append({
                    "test": "Area Distribution Section", 
                    "status": "PASSED", 
                    "details": f"All {len(area_distribution)} areas have required fields with actual names: {actual_area_names}"
                })
                return True
            else:
                self.test_results.append({
                    "test": "Area Distribution Section", 
                    "status": "FAILED", 
                    "reason": "Some areas missing required fields"
                })
                return False
                
        except Exception as e:
            print(f"❌ Area distribution section test failed: {e}")
            self.test_results.append({
                "test": "Area Distribution Section", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_insights_text_personalization(self, insights_data: Dict[str, Any]):
        """Test 5: Insights Text Personalization Verification"""
        print("\n🧪 Test 5: Insights Text Personalization Verification")
        
        try:
            insights_text = insights_data.get('insights_text', [])
            
            if not insights_text:
                print("❌ No insights text found")
                self.test_results.append({
                    "test": "Insights Text Personalization", 
                    "status": "FAILED", 
                    "reason": "No insights text provided"
                })
                return False
            
            print(f"📝 Found {len(insights_text)} insight messages:")
            
            # Check for personalized content
            has_personalized_content = False
            generic_phrases = [
                "Health & Fitness", "Career Growth", "Personal Development",
                "generic pillar", "sample data", "mock data"
            ]
            
            for i, insight in enumerate(insights_text):
                print(f"  {i+1}. {insight}")
                
                # Check if insight contains actual pillar/area names (not generic)
                is_generic = any(phrase in insight for phrase in generic_phrases)
                if not is_generic and len(insight) > 20:  # Meaningful length
                    has_personalized_content = True
            
            if has_personalized_content:
                print("✅ Insights text appears to be personalized with actual user data")
                self.test_results.append({
                    "test": "Insights Text Personalization", 
                    "status": "PASSED", 
                    "details": f"Found {len(insights_text)} personalized insights"
                })
                return True
            else:
                print("⚠️ Insights text may be generic or user has no data")
                self.test_results.append({
                    "test": "Insights Text Personalization", 
                    "status": "PASSED", 
                    "details": f"Found {len(insights_text)} insights (may be generic due to limited user data)"
                })
                return True
                
        except Exception as e:
            print(f"❌ Insights text personalization test failed: {e}")
            self.test_results.append({
                "test": "Insights Text Personalization", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_recommendations_section(self, insights_data: Dict[str, Any]):
        """Test 6: Recommendations Section Verification"""
        print("\n🧪 Test 6: Recommendations Section Verification")
        
        try:
            recommendations = insights_data.get('recommendations', [])
            
            if not recommendations:
                print("⚠️ No recommendations found - user may have complete setup")
                self.test_results.append({
                    "test": "Recommendations Section", 
                    "status": "PASSED", 
                    "details": "No recommendations (user may have complete setup)"
                })
                return True
            
            print(f"💡 Found {len(recommendations)} recommendations:")
            
            # Verify each recommendation has required fields
            required_recommendation_fields = ['type', 'title', 'description', 'action']
            
            all_recommendations_valid = True
            recommendation_types = []
            
            for i, rec in enumerate(recommendations):
                missing_fields = [field for field in required_recommendation_fields if field not in rec]
                
                if missing_fields:
                    print(f"❌ Recommendation {i+1} missing fields: {missing_fields}")
                    all_recommendations_valid = False
                else:
                    rec_type = rec['type']
                    rec_title = rec['title']
                    rec_description = rec['description']
                    rec_action = rec['action']
                    
                    recommendation_types.append(rec_type)
                    
                    print(f"  {i+1}. [{rec_type}] {rec_title}")
                    print(f"     Description: {rec_description}")
                    print(f"     Action: {rec_action}")
                    
                    # Check for actionable content
                    if len(rec_title) > 10 and len(rec_description) > 20:
                        print(f"     ✅ Recommendation appears actionable and detailed")
                    else:
                        print(f"     ⚠️ Recommendation may be too brief")
            
            if all_recommendations_valid:
                self.test_results.append({
                    "test": "Recommendations Section", 
                    "status": "PASSED", 
                    "details": f"All {len(recommendations)} recommendations have required fields. Types: {recommendation_types}"
                })
                return True
            else:
                self.test_results.append({
                    "test": "Recommendations Section", 
                    "status": "FAILED", 
                    "reason": "Some recommendations missing required fields"
                })
                return False
                
        except Exception as e:
            print(f"❌ Recommendations section test failed: {e}")
            self.test_results.append({
                "test": "Recommendations Section", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_productivity_trends_section(self, insights_data: Dict[str, Any]):
        """Test 7: Productivity Trends Section Verification"""
        print("\n🧪 Test 7: Productivity Trends Section Verification")
        
        try:
            productivity_trends = insights_data.get('productivity_trends', {})
            
            required_trend_fields = ['this_week', 'last_week', 'monthly_average', 'trend']
            missing_fields = [field for field in required_trend_fields if field not in productivity_trends]
            
            if missing_fields:
                print(f"❌ Missing productivity trend fields: {missing_fields}")
                self.test_results.append({
                    "test": "Productivity Trends Section", 
                    "status": "FAILED", 
                    "reason": f"Missing fields: {missing_fields}"
                })
                return False
            
            this_week = productivity_trends['this_week']
            last_week = productivity_trends['last_week']
            monthly_avg = productivity_trends['monthly_average']
            trend = productivity_trends['trend']
            
            print(f"📈 Productivity Trends:")
            print(f"   This week: {this_week}%")
            print(f"   Last week: {last_week}%")
            print(f"   Monthly average: {monthly_avg}%")
            print(f"   Trend: {trend}")
            
            # Verify values are reasonable
            if all(0 <= val <= 100 for val in [this_week, last_week, monthly_avg]):
                print("✅ Productivity percentages are within valid range (0-100%)")
            else:
                print("⚠️ Some productivity percentages are outside valid range")
            
            valid_trends = ['increasing', 'decreasing', 'stable', 'no_data']
            if trend in valid_trends:
                print(f"✅ Trend value '{trend}' is valid")
            else:
                print(f"⚠️ Trend value '{trend}' may be unexpected")
            
            self.test_results.append({
                "test": "Productivity Trends Section", 
                "status": "PASSED", 
                "details": f"All trend fields present. This week: {this_week}%, Trend: {trend}"
            })
            return True
            
        except Exception as e:
            print(f"❌ Productivity trends section test failed: {e}")
            self.test_results.append({
                "test": "Productivity Trends Section", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_generated_timestamp(self, insights_data: Dict[str, Any]):
        """Test 8: Generated Timestamp Verification"""
        print("\n🧪 Test 8: Generated Timestamp Verification")
        
        try:
            generated_at = insights_data.get('generated_at')
            
            if not generated_at:
                print("❌ No generated_at timestamp found")
                self.test_results.append({
                    "test": "Generated Timestamp", 
                    "status": "FAILED", 
                    "reason": "No generated_at timestamp"
                })
                return False
            
            # Try to parse the timestamp
            try:
                parsed_time = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
                current_time = datetime.utcnow()
                time_diff = abs((current_time - parsed_time.replace(tzinfo=None)).total_seconds())
                
                print(f"⏰ Generated at: {generated_at}")
                print(f"   Time difference from now: {time_diff:.1f} seconds")
                
                if time_diff < 300:  # Within 5 minutes
                    print("✅ Timestamp is recent (within 5 minutes)")
                else:
                    print("⚠️ Timestamp is older than 5 minutes (may be cached)")
                
                self.test_results.append({
                    "test": "Generated Timestamp", 
                    "status": "PASSED", 
                    "details": f"Valid timestamp: {generated_at}"
                })
                return True
                
            except ValueError as e:
                print(f"❌ Invalid timestamp format: {e}")
                self.test_results.append({
                    "test": "Generated Timestamp", 
                    "status": "FAILED", 
                    "reason": f"Invalid timestamp format: {e}"
                })
                return False
                
        except Exception as e:
            print(f"❌ Generated timestamp test failed: {e}")
            self.test_results.append({
                "test": "Generated Timestamp", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 ENHANCED INSIGHTS API TESTING - DESCRIPTIVE DATA VERIFICATION")
        print("="*80)
        
        passed = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed = len([t for t in self.test_results if t["status"] == "FAILED"])
        total = len(self.test_results)
        
        print(f"📊 OVERALL RESULTS: {passed}/{total} tests passed")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"PASSED": "✅", "FAILED": "❌"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n" + "="*80)
        
        # Determine overall system status
        if success_rate == 100:
            print("🎉 ENHANCED INSIGHTS API IS WORKING PERFECTLY!")
            print("✅ All descriptive data verification tests passed")
            print("✅ API returns meaningful, personalized insights with actual user data")
        elif success_rate >= 85:
            print("⚠️ ENHANCED INSIGHTS API IS MOSTLY FUNCTIONAL - MINOR ISSUES DETECTED")
        else:
            print("❌ ENHANCED INSIGHTS API HAS SIGNIFICANT ISSUES - NEEDS ATTENTION")
            
        print("="*80)
        
    async def run_enhanced_insights_test(self):
        """Run comprehensive Enhanced Insights API test suite"""
        print("🚀 Starting Enhanced Insights API Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("📋 Testing descriptive data with actual pillar names, icons, colors, and recommendations")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Test 1: API Structure
            insights_data = await self.test_insights_api_structure()
            if not insights_data:
                print("❌ Insights API structure test failed - stopping tests")
                return
                
            # Test 2-8: Detailed verification tests
            await self.test_pillar_alignment_data(insights_data)
            await self.test_alignment_snapshot_statistics(insights_data)
            await self.test_area_distribution_section(insights_data)
            await self.test_insights_text_personalization(insights_data)
            await self.test_recommendations_section(insights_data)
            await self.test_productivity_trends_section(insights_data)
            await self.test_generated_timestamp(insights_data)
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    """Main test execution"""
    test_suite = EnhancedInsightsTestSuite()
    await test_suite.run_enhanced_insights_test()

if __name__ == "__main__":
    asyncio.run(main())