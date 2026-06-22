from app.llm.prompts.analysis_prompt import ANALYSIS_PROMPT

def test_prompt_not_empty():
    assert len(ANALYSIS_PROMPT) > 0