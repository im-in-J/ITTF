"""에이전트 공통 베이스 — Claude API Tool Use 루프"""

import anthropic
from backend.config import ANTHROPIC_API_KEY


client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


async def run_agent_loop(
    system_prompt: str,
    user_prompt: str,
    tools: list[dict],
    tool_executor: callable,
    model: str = "claude-sonnet-4-6",
    max_turns: int = 30,
) -> dict:
    """Claude Tool Use 에이전트 루프.

    1. Claude에게 시스템 프롬프트 + 도구 목록을 보낸다.
    2. Claude가 tool_use로 응답하면, tool_executor로 실행하고 결과를 돌려보낸다.
    3. Claude가 text로 최종 응답하면 종료한다.

    Returns:
        {
            "result": str (Claude의 최종 텍스트 응답),
            "tokens_input": int,
            "tokens_output": int,
            "turns": int,
        }
    """
    messages = [{"role": "user", "content": user_prompt}]
    total_input_tokens = 0
    total_output_tokens = 0

    for turn in range(max_turns):
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            tools=tools,
            messages=messages,
        )

        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        # Claude의 응답을 메시지에 추가
        messages.append({"role": "assistant", "content": response.content})

        # tool_use가 없으면 종료 (최종 응답)
        if response.stop_reason == "end_turn":
            final_text = ""
            for block in response.content:
                if block.type == "text":
                    final_text += block.text
            return {
                "result": final_text,
                "tokens_input": total_input_tokens,
                "tokens_output": total_output_tokens,
                "turns": turn + 1,
            }

        # tool_use 블록 처리
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = await tool_executor(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })

        if tool_results:
            messages.append({"role": "user", "content": tool_results})

    return {
        "result": "최대 턴 수에 도달하여 중단되었습니다.",
        "tokens_input": total_input_tokens,
        "tokens_output": total_output_tokens,
        "turns": max_turns,
    }
