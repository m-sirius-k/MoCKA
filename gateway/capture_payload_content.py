# -*- coding: utf-8 -*-
"""
FINAL PAYLOAD OBSERVATION
Capture the actual request_text that reaches adapter_gpt.call_api()
WITHOUT modifying adapter_gpt.py or multi_dispatcher.py

Method: Monkey-patch OpenAI client to intercept payload before API call
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Global store for intercepted payloads
intercepted_payloads = []

def intercept_openai_call():
    """
    Monkey-patch the OpenAI client to intercept messages before API call.
    This is a READ-ONLY interception, not a modification.
    """
    try:
        from openai import OpenAI
        original_create = OpenAI.chat.completions.create

        def create_with_capture(self, *args, **kwargs):
            # Capture payload BEFORE it goes to OpenAI
            messages = kwargs.get('messages', [])
            model = kwargs.get('model', 'unknown')

            if messages and len(messages) > 0:
                user_message_content = messages[0].get('content', '')
                intercepted_payloads.append({
                    "model": model,
                    "messages_count": len(messages),
                    "first_message_role": messages[0].get('role'),
                    "first_message_content": user_message_content,
                    "content_length": len(user_message_content),
                    "timestamp": json.dumps({
                        "captured_at": str(Path(__file__).parent)
                    })
                })

                print(f"\n[INTERCEPTED] OpenAI API payload BEFORE call:")
                print(f"  Model: {model}")
                print(f"  Messages: {len(messages)}")
                print(f"  First message role: {messages[0].get('role')}")
                print(f"  Content length: {len(user_message_content)} chars")

                # Check for Decision context markers
                has_decision_context = "[JARVIS DECISION CONTEXT]" in user_message_content
                has_end_marker = "[END JARVIS DECISION CONTEXT]" in user_message_content

                print(f"\n  Decision context block present: {has_decision_context}")
                print(f"  End marker present: {has_end_marker}")

                if has_decision_context:
                    # Extract the decision block
                    start_idx = user_message_content.find("[JARVIS DECISION CONTEXT]")
                    end_idx = user_message_content.find("[END JARVIS DECISION CONTEXT]")
                    if start_idx >= 0 and end_idx >= 0:
                        decision_block = user_message_content[start_idx:end_idx + len("[END JARVIS DECISION CONTEXT]")]
                        print(f"\n  Decision block content:")
                        for line in decision_block.split('\n')[:10]:  # First 10 lines
                            if line.strip():
                                print(f"    {line[:70]}")

                # Check for Original request marker
                has_original = "Original request:" in user_message_content
                print(f"\n  Original request section present: {has_original}")

                # Store for verification
                intercepted_payloads[-1]["has_decision_context"] = has_decision_context
                intercepted_payloads[-1]["has_end_marker"] = has_end_marker
                intercepted_payloads[-1]["has_original_request"] = has_original

                # Extract Decision ID
                decision_id_line = [line for line in user_message_content.split('\n') if 'Decision ID:' in line]
                if decision_id_line:
                    intercepted_payloads[-1]["decision_id"] = decision_id_line[0].strip()
                    print(f"\n  {decision_id_line[0].strip()}")

            # Call original OpenAI API
            return original_create(self, *args, **kwargs)

        # Apply the monkey-patch
        OpenAI.chat.completions.create = create_with_capture
        print("[SETUP] OpenAI.chat.completions.create intercepted for payload capture")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to set up interception: {e}")
        return False


def main():
    print("\n" + "="*70)
    print("FINAL PAYLOAD OBSERVATION")
    print("Capture actual request_text in OpenAI payload")
    print("="*70)

    # Setup interception
    if not intercept_openai_call():
        print("ERROR: Could not set up interception")
        return 1

    # Import AFTER monkey-patching
    from multi_dispatcher import dispatch_multi_request

    print("\n[EXECUTE] Calling dispatch_multi_request() with decision_id...")

    try:
        result = dispatch_multi_request(
            request_text="Verify payload content with Decision context",
            providers=["gpt"],
            decision_id="PAYLOAD_VERIFY_001"
        )

        print(f"\n[RESULT] dispatch_multi_request completed")
        print(f"  Status: {result.get('status')}")
        print(f"  JARVIS status: {result.get('jarvis', {}).get('status')}")
        print(f"  GPT result status: {result.get('results', [{}])[0].get('status') if result.get('results') else 'N/A'}")

    except Exception as e:
        print(f"[ERROR] dispatch_multi_request failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Analysis
    print("\n" + "="*70)
    print("PAYLOAD VERIFICATION RESULTS")
    print("="*70)

    if not intercepted_payloads:
        print("[RESULT] No payloads intercepted")
        print("STATUS: UNKNOWN (no payload observation)")
        return 1

    payload = intercepted_payloads[0]

    print(f"\nPayload 1:")
    print(f"  Model: {payload.get('model')}")
    print(f"  Content length: {payload.get('content_length')} chars")
    print(f"  Has Decision context block: {payload.get('has_decision_context')}")
    print(f"  Has end marker: {payload.get('has_end_marker')}")
    print(f"  Has original request: {payload.get('has_original_request')}")
    print(f"  Decision ID captured: {payload.get('decision_id', 'N/A')}")

    # Final verdict
    verified = (
        payload.get('has_decision_context') and
        payload.get('has_end_marker') and
        payload.get('has_original_request') and
        payload.get('decision_id')
    )

    print("\n" + "="*70)
    if verified:
        print("PAYLOAD VERIFICATION: VERIFIED")
        print("\nEvidence:")
        print(f"  [+] Decision context block present in messages[].content")
        print(f"  [+] End marker present")
        print(f"  [+] Original request preserved")
        print(f"  [+] Real Decision ID embedded: {payload.get('decision_id')}")
        print(f"\nConclusion: Enhanced request_text successfully reached OpenAI API payload")
        return 0
    else:
        print("PAYLOAD VERIFICATION: UNKNOWN")
        print("\nMissing evidence:")
        if not payload.get('has_decision_context'):
            print(f"  [-] No Decision context block")
        if not payload.get('has_end_marker'):
            print(f"  [-] No end marker")
        if not payload.get('has_original_request'):
            print(f"  [-] No original request")
        return 1


if __name__ == "__main__":
    sys.exit(main())
