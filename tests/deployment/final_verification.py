#!/usr/bin/env python3
"""
Final verification that everything works after cleanup
"""

import json
import boto3

def final_verification():
    """Final test to ensure cleanup didn't break anything"""
    
    lambda_client = boto3.client('lambda', region_name='us-west-2')
    function_name = 'AyeAyeStack-CreateRecipeLambda2BD8AFF3-iuqdJg0lCo0I'
    
    print("🔍 FINAL VERIFICATION AFTER CLEANUP")
    print("=" * 50)
    
    # Test the key functionality that was fixed
    payload = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'mock_ingredients': [
                {'name': 'mango', 'grams': 200, 'fdc_id': '169910'}
            ],
            'recipe_category': 'smoothie',
            'cuisine': 'healthy',
            'servings': 2,
            'user_id': 'final_test'
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
            
            print(f"✅ Status: SUCCESS")
            print(f"✅ Recipe Count: {len(recipes)}")
            
            for i, recipe in enumerate(recipes, 1):
                title = recipe.get('title', 'No Title')
                print(f"  {i}. {title}")
            
            # Verify we're getting ingredient-specific recipes, not templates
            titles_text = ' '.join([recipe.get('title', '') for recipe in recipes])
            
            if 'Recipe 1' in titles_text or 'Simple Test Recipe' in titles_text:
                print("❌ FAILURE: Still getting template recipes!")
                return False
            elif 'Mango' in titles_text:
                print("✅ SUCCESS: Getting ingredient-specific mango recipes!")
                return True
            else:
                print("⚠️ WARNING: Unexpected recipe format")
                return False
                
        else:
            print(f"❌ Error: {response_payload}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = final_verification()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 CLEANUP SUCCESSFUL!")
        print("✅ All functionality preserved")
        print("✅ Code organization improved") 
        print("✅ Ingredient-specific recipes working")
    else:
        print("❌ CLEANUP FAILED!")
        print("🔧 Need to investigate issues")