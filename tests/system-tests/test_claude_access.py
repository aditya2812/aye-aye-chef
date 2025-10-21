#!/usr/bin/env python3
"""
Quick test to check if Claude Vision access is working
"""
import boto3
import json

def test_claude_access():
    """Test if we can access Claude models"""
    try:
        bedrock = boto3.client('bedrock-runtime')
        
        # Simple text test first
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 100,
                'messages': [{
                    'role': 'user',
                    'content': 'Hello! Can you respond with "Claude access is working"?'
                }]
            })
        )
        
        result = json.loads(response['body'].read())
        ai_response = result['content'][0]['text']
        
        print("✅ SUCCESS: Claude access is working!")
        print(f"Response: {ai_response}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Claude access not working: {e}")
        return False

if __name__ == "__main__":
    test_claude_access()