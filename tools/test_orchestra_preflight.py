"""
TODO_166: Orchestra UI Blocker Detection — Unit Tests
テスト対象: preflight_check() 関数の各種ブロッカー検知能力
"""

import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, '/home/user/MoCKA/tools')

async def test_preflight_ready():
    """正常系: 入力フィールドが ready 状態"""
    print("TEST 1: Normal Case (READY)")

    mock_page = MagicMock()
    mock_field = AsyncMock()

    mock_page.query_selector = AsyncMock(side_effect=[None] * 6)  # No CAPTCHA, no dialogs
    mock_page.locator = MagicMock(return_value=MagicMock(first=mock_field))

    mock_field.wait_for = AsyncMock()  # No exception = field is ready

    # Import after mocking setup
    import mocka_orchestra_v10
    result = await mocka_orchestra_v10.preflight_check(mock_page, "TestAI")

    assert result["status"] == "READY", f"Expected READY, got {result['status']}"
    print("  ✓ READY detection working")


async def test_preflight_captcha():
    """ブロッカー: CAPTCHA検知"""
    print("TEST 2: CAPTCHA Blocker")

    mock_page = MagicMock()
    mock_page.query_selector = AsyncMock(return_value=MagicMock())  # CAPTCHA found

    import mocka_orchestra_v10
    result = await mocka_orchestra_v10.preflight_check(mock_page, "Copilot")

    assert result["status"] == "BLOCKED_CAPTCHA", f"Expected BLOCKED_CAPTCHA, got {result['status']}"
    print("  ✓ CAPTCHA detection working")


async def test_preflight_dialog():
    """ブロッカー: ダイアログ検知"""
    print("TEST 3: Dialog Blocker")

    mock_page = MagicMock()
    mock_page.query_selector = AsyncMock(side_effect=[None])  # No CAPTCHA
    mock_page.query_selector_all = AsyncMock(return_value=[MagicMock()])  # Dialog found

    import mocka_orchestra_v10
    result = await mocka_orchestra_v10.preflight_check(mock_page, "Perplexity")

    assert result["status"] == "BLOCKED_DIALOG", f"Expected BLOCKED_DIALOG, got {result['status']}"
    print("  ✓ Dialog detection working")


async def test_preflight_error():
    """エラー系: 入力フィールド未検出"""
    print("TEST 4: Input Field Not Found")

    mock_page = MagicMock()
    mock_page.query_selector = AsyncMock(return_value=None)
    mock_page.query_selector_all = AsyncMock(return_value=[])

    mock_field = AsyncMock()
    mock_field.wait_for = AsyncMock(side_effect=Exception("Timeout"))
    mock_page.locator = MagicMock(return_value=MagicMock(first=mock_field))

    import mocka_orchestra_v10
    result = await mocka_orchestra_v10.preflight_check(mock_page, "Claude")

    assert result["status"] == "ERROR", f"Expected ERROR, got {result['status']}"
    print("  ✓ Error handling working")


async def run_tests():
    """すべてのテストを実行"""
    print("=" * 60)
    print("TODO_166: Preflight Check Unit Tests")
    print("=" * 60)

    try:
        await test_preflight_ready()
        await test_preflight_captcha()
        await test_preflight_dialog()
        await test_preflight_error()

        print("\n" + "=" * 60)
        print("✓ All tests passed")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
