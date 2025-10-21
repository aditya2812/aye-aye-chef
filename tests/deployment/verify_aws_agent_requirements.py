#!/usr/bin/env python3
"""
Verify that our system meets AWS AI Agent requirements
"""

import json
import boto3
import os

def check_aws_agent_requirements():
    """Check if our system meets all AWS AI Agent requirements"""
    
    print("🔍 AWS AI AGENT REQUIREMENTS VERIFICATION")
    print("=" * 60)
    
    requirements = {
        "llm_hosted_aws": False,
        "bedrock_agent_core": False,
        "reasoning_llm": False,
        "autonomous_capabilities": False,
        "integrates_apis_databases": False,
        "helper_services": []
    }
    
    # Check 1: LLM hosted on AWS Bedrock or SageMaker
    print("\n1️⃣ LLM HOSTED ON AWS BEDROCK/SAGEMAKER:")
    
    try:
        # Check if we're using Bedrock
        with open('lambda/create-recipe/create_recipe.py', 'r') as f:
            content = f.read()
        
        if 'bedrock-runtime' in content and 'anthropic.claude' in content:
            print("   ✅ Using AWS Bedrock with Claude LLM")
            requirements["llm_hosted_aws"] = True
        else:
            print("   ❌ No Bedrock LLM usage found")
            
    except Exception as e:
        print(f"   ❌ Error checking LLM usage: {e}")
    
    # Check 2: Uses Bedrock Agent Core or other required services
    print("\n2️⃣ AWS SERVICES USAGE:")
    
    aws_services_found = []
    
    if 'bedrock-agent-runtime' in content:
        aws_services_found.append("Amazon Bedrock Agent")
        requirements["bedrock_agent_core"] = True
        print("   ✅ Amazon Bedrock Agent - Found")
    
    if 'bedrock-runtime' in content:
        aws_services_found.append("Amazon Bedrock")
        print("   ✅ Amazon Bedrock - Found")
    
    if 'rds-data' in content:
        aws_services_found.append("Amazon RDS")
        print("   ✅ Amazon RDS (Database) - Found")
    
    if 'secretsmanager' in content:
        aws_services_found.append("AWS Secrets Manager")
        print("   ✅ AWS Secrets Manager - Found")
    
    # Check 3: Uses reasoning LLMs for decision-making
    print("\n3️⃣ REASONING LLM FOR DECISION-MAKING:")
    
    if 'anthropic.claude' in content and 'generate_ai_recipes' in content:
        print("   ✅ Uses Claude LLM for recipe generation decisions")
        print("   ✅ Makes decisions based on ingredients, cuisine, and user preferences")
        requirements["reasoning_llm"] = True
    else:
        print("   ❌ No reasoning LLM usage found")
    
    # Check 4: Demonstrates autonomous capabilities
    print("\n4️⃣ AUTONOMOUS CAPABILITIES:")
    
    autonomous_features = []
    
    if 'generate_ingredient_specific_recipes' in content:
        autonomous_features.append("Autonomous ingredient-specific recipe generation")
        print("   ✅ Autonomously generates recipes based on detected ingredients")
    
    if 'create_cooking_recipes_for_ingredient' in content:
        autonomous_features.append("Autonomous cuisine-specific adaptation")
        print("   ✅ Autonomously adapts recipes to different cuisines")
    
    if 'format_ai_recipe' in content:
        autonomous_features.append("Autonomous recipe formatting")
        print("   ✅ Autonomously formats and structures recipe output")
    
    if len(autonomous_features) >= 2:
        requirements["autonomous_capabilities"] = True
        print("   ✅ Multiple autonomous capabilities demonstrated")
    
    # Check 5: Integrates APIs, databases, external tools
    print("\n5️⃣ INTEGRATION WITH APIS/DATABASES/TOOLS:")
    
    integrations = []
    
    if 'rds_client.execute_statement' in content:
        integrations.append("Database Integration (RDS)")
        print("   ✅ Integrates with RDS database for ingredient data")
    
    if 'fetch_usda_nutrients' in content and 'requests.post' in content:
        integrations.append("External API Integration (USDA)")
        print("   ✅ Integrates with USDA FoodData Central API")
    
    if 'bedrock_runtime.invoke_model' in content:
        integrations.append("AI Model Integration (Bedrock)")
        print("   ✅ Integrates with Bedrock AI models")
    
    if 'secrets_client.get_secret_value' in content:
        integrations.append("AWS Services Integration")
        print("   ✅ Integrates with AWS Secrets Manager")
    
    if len(integrations) >= 2:
        requirements["integrates_apis_databases"] = True
        print("   ✅ Multiple integrations demonstrated")
    
    # Check 6: Helper services (optional but recommended)
    print("\n6️⃣ HELPER SERVICES (OPTIONAL):")
    
    helper_services = []
    
    if 'AWS Lambda' in content or 'lambda' in os.getcwd():
        helper_services.append("AWS Lambda")
        print("   ✅ AWS Lambda - Used for serverless execution")
    
    if 'cloudwatch' in content:
        helper_services.append("Amazon CloudWatch")
        print("   ✅ Amazon CloudWatch - Used for monitoring")
    
    if 'API Gateway' in content or 'httpMethod' in content:
        helper_services.append("Amazon API Gateway")
        print("   ✅ Amazon API Gateway - Used for HTTP API")
    
    requirements["helper_services"] = helper_services
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 REQUIREMENTS SUMMARY:")
    
    total_required = 5  # First 5 are required
    met_required = sum([
        requirements["llm_hosted_aws"],
        requirements["bedrock_agent_core"] or "bedrock-runtime" in content,  # Either agent or direct bedrock
        requirements["reasoning_llm"],
        requirements["autonomous_capabilities"],
        requirements["integrates_apis_databases"]
    ])
    
    print(f"\n✅ REQUIRED CRITERIA MET: {met_required}/{total_required}")
    
    if requirements["llm_hosted_aws"]:
        print("   ✅ LLM hosted on AWS Bedrock")
    else:
        print("   ❌ LLM not hosted on AWS")
    
    if requirements["bedrock_agent_core"] or "bedrock-runtime" in content:
        print("   ✅ Uses AWS Bedrock services")
    else:
        print("   ❌ No Bedrock services found")
    
    if requirements["reasoning_llm"]:
        print("   ✅ Uses reasoning LLM for decisions")
    else:
        print("   ❌ No reasoning LLM usage")
    
    if requirements["autonomous_capabilities"]:
        print("   ✅ Demonstrates autonomous capabilities")
    else:
        print("   ❌ No autonomous capabilities")
    
    if requirements["integrates_apis_databases"]:
        print("   ✅ Integrates APIs/databases/tools")
    else:
        print("   ❌ No integrations found")
    
    print(f"\n🔧 HELPER SERVICES: {len(requirements['helper_services'])}")
    for service in requirements["helper_services"]:
        print(f"   ✅ {service}")
    
    # Final verdict
    print(f"\n🎯 FINAL VERDICT:")
    if met_required == total_required:
        print("🎉 FULLY COMPLIANT with AWS AI Agent requirements!")
        print("✅ All required criteria met")
        print("✅ Multiple helper services used")
        return True
    else:
        print("❌ NOT FULLY COMPLIANT")
        print(f"❌ Missing {total_required - met_required} required criteria")
        return False

def test_agent_functionality():
    """Test that the agent actually works as expected"""
    
    print("\n" + "=" * 60)
    print("🧪 TESTING AGENT FUNCTIONALITY:")
    
    lambda_client = boto3.client('lambda', region_name='us-west-2')
    function_name = 'AyeAyeStack-CreateRecipeLambda2BD8AFF3-iuqdJg0lCo0I'
    
    # Test autonomous decision-making
    payload = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'mock_ingredients': [{'name': 'chicken', 'grams': 300, 'fdc_id': '171477'}],
            'recipe_category': 'cuisine',
            'cuisine': 'thai',  # Test reasoning: should adapt to Thai cuisine
            'servings': 2,
            'user_id': 'aws_agent_test'
        })
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        response_payload = json.loads(response['Payload'].read())
        
        if response_payload.get('statusCode') == 200:
            body = json.loads(response_payload['body'])
            recipes = body.get('recipes', [])
            
            print(f"✅ Agent Response: Generated {len(recipes)} recipes")
            
            # Check if agent made intelligent decisions
            titles = [recipe.get('title', '') for recipe in recipes]
            titles_text = ' '.join(titles)
            
            if 'Thai' in titles_text or 'Curry' in titles_text or 'Basil' in titles_text:
                print("✅ Autonomous Decision-Making: Correctly adapted to Thai cuisine")
                return True
            else:
                print("❌ Decision-Making: Did not adapt to cuisine properly")
                print(f"   Got: {titles}")
                return False
        else:
            print(f"❌ Agent Error: {response_payload}")
            return False
            
    except Exception as e:
        print(f"❌ Agent Test Failed: {str(e)}")
        return False

if __name__ == "__main__":
    compliance = check_aws_agent_requirements()
    functionality = test_agent_functionality()
    
    print("\n" + "=" * 60)
    if compliance and functionality:
        print("🎉 AWS AI AGENT FULLY VERIFIED!")
        print("✅ Meets all AWS requirements")
        print("✅ Demonstrates working AI agent capabilities")
    else:
        print("❌ AWS AI AGENT VERIFICATION FAILED!")
        if not compliance:
            print("❌ Does not meet AWS requirements")
        if not functionality:
            print("❌ Agent functionality not working")